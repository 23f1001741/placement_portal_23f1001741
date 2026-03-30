import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../components/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../components/Login.vue')
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../components/AdminDashboard.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/company',
    name: 'CompanyDashboard',
    component: () => import('../components/CompanyDashboard.vue'),
    meta: { requiresAuth: true, role: 'company' }
  },
  {
    path: '/student',
    name: 'StudentDashboard',
    component: () => import('../components/StudentDashboard.vue'),
    meta: { requiresAuth: true, role: 'student' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// --- Navigation Guard ---
// This is the logic that makes the "Logout" button actually change the screen
router.beforeEach((to, from, next) => {
  // CHANGED: Use 'token' to match your Login.vue
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('role');

  if (to.meta.requiresAuth) {
    if (!token) return next('/login');
    if (to.meta.role && to.meta.role !== userRole) return next('/login');
  }

  if (to.path === '/login' && token) {
    if (userRole === 'admin') return next('/admin');
    if (userRole === 'company') return next('/company');
    if (userRole === 'student') return next('/student');
  }

  next();
});

export default router
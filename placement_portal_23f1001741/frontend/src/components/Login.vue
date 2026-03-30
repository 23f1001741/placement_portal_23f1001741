<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card shadow">
          <div class="card-header text-center bg-primary text-white">
            <h4>{{ isLogin ? 'Sign In' : 'Register Account' }}</h4>
          </div>
          <div class="card-body">
            
            <div v-if="message" :class="['alert', isError ? 'alert-danger' : 'alert-success']">
              {{ message }}
            </div>

            <form @submit.prevent="handleSubmit">
              
              <div v-if="!isLogin">
                <div class="mb-3">
                  <label class="form-label">Username</label>
                  <input type="text" class="form-control" v-model="formData.username" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">I am a...</label>
                  <select class="form-select" v-model="formData.role" required>
                    <option value="student">Student</option>
                    <option value="company">Company</option>
                  </select>
                </div>
              </div>

              <div v-if="!isLogin && formData.role === 'company'" class="border p-3 mb-3 bg-light">
                <h6>Company Details</h6>
                <div class="mb-2">
                  <label class="form-label">Company Name</label>
                  <input type="text" class="form-control" v-model="formData.company_name" required>
                </div>
                <div class="mb-2">
                  <label class="form-label">HR Contact Name</label>
                  <input type="text" class="form-control" v-model="formData.hr_contact" required>
                </div>
                <div class="mb-2">
                  <label class="form-label">Website</label>
                  <input type="text" class="form-control" v-model="formData.website">
                </div>
              </div>

              <div v-if="!isLogin && formData.role === 'student'" class="border p-3 mb-3 bg-light">
                <h6>Student Details</h6>
                <div class="mb-2">
                  <label class="form-label">Branch</label>
                  <input type="text" class="form-control" v-model="formData.branch" required>
                </div>
                <div class="mb-2">
                  <label class="form-label">CGPA</label>
                  <input type="number" step="0.01" class="form-control" v-model="formData.cgpa" required>
                </div>
                <div class="mb-2">
                  <label class="form-label">Graduation Year</label>
                  <input type="number" class="form-control" v-model="formData.graduation_year" required>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Email address</label>
                <input type="email" class="form-control" v-model="formData.email" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" class="form-control" v-model="formData.password" required>
              </div>

              <button type="submit" class="btn btn-primary w-100">
                {{ isLogin ? 'Login' : 'Register' }}
              </button>
            </form>

            <div class="text-center mt-3">
              <button class="btn btn-link text-decoration-none" @click="toggleMode">
                {{ isLogin ? "Don't have an account? Register here." : "Already have an account? Login here." }}
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      isLogin: true,
      message: '',
      isError: false,
      formData: {
        email: '',
        password: '',
        username: '',
        role: 'student', // Default role for registration
        company_name: '',
        hr_contact: '',
        website: '',
        branch: '',
        cgpa: '',
        graduation_year: ''
      }
    }
  },
  methods: {
    toggleMode() {
      this.isLogin = !this.isLogin;
      this.message = '';
    },
    async handleSubmit() {
      this.message = '';
      const endpoint = this.isLogin ? '/api/auth/login' : '/api/auth/register';
      const url = `http://localhost:5000${endpoint}`;

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.formData)
        });

        const data = await response.json();

        if (response.ok) {
          this.isError = false;
          if (this.isLogin) {
            // Save token and role to local storage
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('role', data.role);
            this.message = 'Login successful! Redirecting...';
            
            // Redirect based on role
            setTimeout(() => {
              if (data.role === 'admin') this.$router.push('/admin');
              else if (data.role === 'company') this.$router.push('/company');
              else if (data.role === 'student') this.$router.push('/student');
            }, 1000);

          } else {
            this.message = 'Registration successful! You can now log in.';
            this.isLogin = true; // Switch back to login view
          }
        } else {
          this.isError = true;
          this.message = data.message || 'An error occurred.';
        }
      } catch (error) {
        this.isError = true;
        this.message = 'Failed to connect to the server. Is the Flask backend running?';
      }
    }
  }
}
</script>
<template>
  <div>
    <nav class="navbar navbar-dark bg-dark mb-4 shadow">
      <div class="container">
        <span class="navbar-brand mb-0 h1">Admin Dashboard</span>
        <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
      </div>
    </nav>

    <div class="container pb-5">
      <div class="row mb-4 text-center">
        <div class="col-md-4" v-for="(val, key) in stats" :key="key">
          <div class="card shadow-sm border-primary">
            <div class="card-body">
              <h5 class="card-title text-capitalize">{{ key.replace('_', ' ') }}</h5>
              <h2 class="display-4">{{ val }}</h2>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-5">
        <div class="col-md-12">
          <div class="card shadow-sm p-4">
            <h4 class="border-bottom pb-2">Placement Funnel Performance</h4>
            <canvas id="placementChart" style="max-height: 250px;"></canvas>
          </div>
        </div>
      </div>

      <div class="row mb-5">
        <div class="col-md-6">
          <h4 class="border-bottom pb-2 text-warning">Pending Company Registrations</h4>
          <div class="table-responsive bg-white rounded shadow-sm border" style="max-height: 300px;">
            <table class="table table-sm table-hover mb-0">
              <thead class="table-warning sticky-top">
                <tr><th>Company Name</th><th>HR Contact</th><th>Actions</th></tr>
              </thead>
              <tbody>
                <tr v-for="comp in pendingCompanies" :key="comp.id">
                  <td>{{ comp.name }}</td>
                  <td>{{ comp.hr_contact }}</td>
                  <td>
                    <button class="btn btn-xs btn-success me-1" @click="updateCompanyStatus(comp.id, 'Approved')">✔</button>
                    <button class="btn btn-xs btn-danger" @click="updateCompanyStatus(comp.id, 'Rejected')">✖</button>
                  </td>
                </tr>
                <tr v-if="pendingCompanies.length === 0">
                  <td colspan="3" class="text-center text-muted p-3">No pending registrations.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="col-md-6">
          <h4 class="border-bottom pb-2 text-warning">Pending Placement Drives</h4>
          <div class="table-responsive bg-white rounded shadow-sm border" style="max-height: 300px;">
            <table class="table table-sm table-hover mb-0">
              <thead class="table-warning sticky-top">
                <tr><th>Job Title</th><th>Company</th><th>Actions</th></tr>
              </thead>
              <tbody>
                <tr v-for="drive in pendingDrives" :key="drive.id">
                  <td>{{ drive.job_title }}</td>
                  <td>{{ drive.company_name }}</td>
                  <td>
                    <button class="btn btn-xs btn-success me-1" @click="updateDriveStatus(drive.id, 'Approved')">✔</button>
                    <button class="btn btn-xs btn-danger" @click="updateDriveStatus(drive.id, 'Rejected')">✖</button>
                  </td>
                </tr>
                <tr v-if="pendingDrives.length === 0">
                  <td colspan="3" class="text-center text-muted p-3">No pending drives.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="row mb-5">
        <div class="col-md-12">
          <div class="card shadow-sm">
            <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">User Management</h5>
              <div class="input-group w-50">
                <input type="text" class="form-control form-control-sm" v-model="userSearch" placeholder="Search..." @keyup.enter="fetchUsers">
                <button class="btn btn-primary btn-sm" @click="fetchUsers">Search</button>
              </div>
            </div>
            <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light sticky-top">
                  <tr><th>User</th><th>Role</th><th>Status</th><th>Action</th></tr>
                </thead>
                <tbody>
                  <tr v-for="user in allUsers" :key="user.id">
                    <td>{{ user.username }} <br><small class="text-muted">{{ user.email }}</small></td>
                    <td><span class="badge bg-light text-dark border">{{ user.role }}</span></td>
                    <td><span :class="user.is_active ? 'text-success' : 'text-danger'">● {{ user.is_active ? 'Active' : 'Banned' }}</span></td>
                    <td>
                      <button @click="toggleUserStatus(user.id)" class="btn btn-sm" :class="user.is_active ? 'btn-outline-danger' : 'btn-outline-success'">
                        {{ user.is_active ? 'Deactivate' : 'Activate' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-5">
        <div class="col-md-6">
          <h4 class="border-bottom pb-2 text-primary">Master Interview Schedule</h4>
          <div class="table-responsive bg-white rounded shadow-sm border" style="max-height: 400px; overflow-y: auto;">
            <table class="table table-sm table-striped mb-0">
              <thead class="table-primary sticky-top">
                <tr><th>Date</th><th>Student</th><th>Company</th></tr>
              </thead>
              <tbody>
                <tr v-for="i in globalInterviews" :key="i.id">
                  <td>{{ i.interview_date }}</td>
                  <td>{{ i.student_name }}</td>
                  <td>{{ i.company_name }}</td>
                </tr>
                <tr v-if="globalInterviews.length === 0">
                  <td colspan="3" class="text-center text-muted p-3">No interviews scheduled.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="col-md-6">
          <h4 class="border-bottom pb-2 text-info">Application Tracking</h4>
          <div class="table-responsive bg-white rounded shadow-sm border" style="max-height: 400px; overflow-y: auto;">
            <table class="table table-sm table-striped mb-0">
              <thead class="table-info sticky-top">
                <tr><th>Student</th><th>Company</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="app in allApplications" :key="app.id">
                  <td>{{ app.student_name }}</td>
                  <td>{{ app.company_name }}</td>
                  <td><span :class="statusBadgeClass(app.status)">{{ app.status }}</span></td>
                </tr>
                <tr v-if="allApplications.length === 0">
                  <td colspan="3" class="text-center text-muted p-3">No applications found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  data() {
    return {
      stats: { total_students: 0, total_companies: 0, total_drives: 0 },
      allUsers: [],
      pendingCompanies: [],
      pendingDrives: [],
      globalInterviews: [],
      allApplications: [],
      userSearch: '',
      chartInstance: null
    }
  },
  methods: {
    async fetchDashboardData() {
      const token = localStorage.getItem('token');
      if (!token) { this.logout(); return; }
      const headers = { 'Authorization': `Bearer ${token}` };
      
      try {
        const [sRes, cRes, dRes, iRes, stRes, aRes] = await Promise.all([
          fetch('http://localhost:5000/api/admin/dashboard', { headers }),
          fetch('http://localhost:5000/api/admin/companies/pending', { headers }),
          fetch('http://localhost:5000/api/admin/drives/pending', { headers }),
          fetch('http://localhost:5000/api/admin/interviews', { headers }),
          fetch('http://localhost:5000/api/admin/placement-stats', { headers }),
          fetch('http://localhost:5000/api/admin/applications', { headers })
        ]);
        
        if (sRes.ok) this.stats = await sRes.json();
        if (cRes.ok) this.pendingCompanies = await cRes.json();
        if (dRes.ok) this.pendingDrives = await dRes.json();
        if (iRes.ok) this.globalInterviews = await iRes.json();
        if (aRes.ok) this.allApplications = await aRes.json();
        if (stRes.ok) this.renderChart(await stRes.json());
        
        await this.fetchUsers();
      } catch (err) { console.error(err); }
    },

    async fetchUsers() {
      const token = localStorage.getItem('token');
      const res = await fetch(`http://localhost:5000/api/admin/users?search=${this.userSearch}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) this.allUsers = await res.json();
    },

    async updateCompanyStatus(id, action) {
      const token = localStorage.getItem('token');
      await fetch(`http://localhost:5000/api/admin/companies/${id}/status`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      this.fetchDashboardData();
    },

    async updateDriveStatus(id, action) {
      const token = localStorage.getItem('token');
      await fetch(`http://localhost:5000/api/admin/drives/${id}/status`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      this.fetchDashboardData();
    },

    async toggleUserStatus(userId) {
      const token = localStorage.getItem('token');
      await fetch(`http://localhost:5000/api/admin/users/${userId}/toggle-status`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      this.fetchUsers();
    },

    statusBadgeClass(status) {
      const classes = { 'Selected': 'badge bg-success', 'Rejected': 'badge bg-danger', 'Interview Scheduled': 'badge bg-info text-dark' };
      return classes[status] || 'badge bg-secondary';
    },

    renderChart(data) {
      const ctx = document.getElementById('placementChart');
      if (this.chartInstance) this.chartInstance.destroy();
      this.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Applied', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected'],
          datasets: [{ 
            data: [data.applied, data.shortlisted, data.interviewed, data.selected, data.rejected], 
            backgroundColor: ['#0d6efd', '#ffc107', '#17a2b8', '#198754', '#dc3545'] 
          }]
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false, 
          plugins: { 
            legend: { display: false } 
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1, precision: 0 }
            }
          }
        }
      });
    },

    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      this.$router.push('/login');
    }
  },
  mounted() { this.fetchDashboardData(); }
}
</script>
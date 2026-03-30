<template>
  <div>
    <nav class="navbar navbar-dark bg-info mb-4 shadow">
      <div class="container">
        <span class="navbar-brand mb-0 h1">Student Placement Portal</span>
        <button class="btn btn-dark btn-sm" @click="logout">Logout</button>
      </div>
    </nav>

    <div class="container pb-5">
      <div v-if="message" :class="['alert', isError ? 'alert-danger' : 'alert-success']" class="shadow-sm">
        {{ message }}
      </div>

      <div class="row">
        <div class="col-md-7 mb-4">
          <h4 class="border-bottom pb-2">Explore Opportunities</h4>
          <div class="input-group mb-3 shadow-sm">
            <input type="text" class="form-control" placeholder="Search Role or Company..." v-model="searchQuery" @keyup.enter="fetchDrives">
            <button class="btn btn-primary" @click="fetchDrives">Search</button>
          </div>

          <div v-for="drive in drives" :key="drive.id" class="card mb-3 shadow-sm border-start border-info border-4">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <h5 class="text-info">{{ drive.job_title }}</h5>
                <span v-if="profile.cgpa < drive.minimum_cgpa" class="badge bg-danger">Ineligible</span>
                <span v-else class="badge bg-success">Eligible</span>
              </div>
              <p class="fw-bold mb-1">{{ drive.company_name }}</p>
              <p class="small text-muted mb-2">
                Deadline: {{ drive.deadline }} | 
                <span :class="profile.cgpa < drive.minimum_cgpa ? 'text-danger fw-bold' : ''">
                  Min CGPA: {{ drive.minimum_cgpa }}
                </span>
              </p>
              
              <button 
                v-if="!isAlreadyApplied(drive.id)"
                class="btn btn-sm" 
                :class="profile.cgpa < drive.minimum_cgpa ? 'btn-secondary disabled' : 'btn-primary'"
                @click="applyForDrive(drive.id)"
                :disabled="profile.cgpa < drive.minimum_cgpa"
              >
                {{ profile.cgpa < drive.minimum_cgpa ? 'Criteria Not Met' : 'Apply Now' }}
              </button>
              <button v-else class="btn btn-sm btn-outline-secondary" disabled>Already Applied</button>
            </div>
          </div>
        </div>

        <div class="col-md-5">
          <h4 class="text-primary border-bottom pb-2">Upcoming Interviews</h4>
          <div v-if="upcomingInterviews.length === 0" class="alert alert-light border small py-2 mb-4 text-center">No interviews yet.</div>
          <div v-else class="table-responsive bg-white rounded shadow-sm mb-4">
            <table class="table table-sm table-hover mb-0">
              <thead class="table-primary"><tr><th>Company</th><th>Date & Time</th></tr></thead>
              <tbody>
                <tr v-for="inter in upcomingInterviews" :key="inter.id">
                  <td>{{ inter.company_name }}</td>
                  <td class="fw-bold text-primary small">{{ inter.interview_date }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h4 class="border-bottom pb-2">History</h4>
          <div class="table-responsive bg-white rounded shadow-sm mb-4">
            <table class="table table-sm mb-0">
              <thead><tr class="small"><th>Job</th><th>Status</th></tr></thead>
              <tbody>
                <tr v-for="app in applications" :key="app.id">
                  <td class="small fw-bold">{{ app.job_title }}</td>
                  <td><span class="badge" :class="statusClass(app.status)">{{ app.status }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <h4 class="border-bottom pb-2">My Profile</h4>
          <div class="card shadow-sm p-3 bg-light">
            <div class="mb-2">
              <label class="small fw-bold">Current CGPA</label>
              <input type="number" step="0.01" class="form-control form-control-sm" v-model="profile.cgpa">
            </div>
            <div class="mb-3">
              <label class="small fw-bold">Resume (PDF)</label>
              <input type="file" class="form-control form-control-sm" @change="handleFileUpload">
              <div v-if="profile.resume_url" class="mt-2">
                <a :href="'http://localhost:5000/uploads/resumes/' + profile.resume_url" target="_blank" class="small text-primary text-decoration-none">
                  📄 View My Current Resume
                </a>
              </div>
            </div>
            <button class="btn btn-info btn-sm w-100" @click="updateProfile">Update Profile & Eligibility</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      drives: [], applications: [], searchQuery: '',
      profile: { branch: '', cgpa: 0, resume_url: null },
      message: '', isError: false
    }
  },
  computed: {
    upcomingInterviews() {
      return this.applications.filter(app => app.status === 'Interview Scheduled' && app.interview_date);
    }
  },
  methods: {
    logout() { localStorage.clear(); this.$router.push('/login'); },
    async fetchDrives() {
      const res = await fetch(`http://localhost:5000/api/student/drives?search=${this.searchQuery}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) this.drives = await res.json();
    },
    async fetchProfile() {
      const res = await fetch('http://localhost:5000/api/student/profile', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) this.profile = await res.json();
    },
    async updateProfile() {
      const res = await fetch('http://localhost:5000/api/student/profile', {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(this.profile)
      });
      if (res.ok) {
          this.showMessage("Profile updated!", false);
          this.fetchDrives();
      }
    },
    async applyForDrive(id) {
        const res = await fetch('http://localhost:5000/api/student/applications', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ drive_id: id })
        });
        const data = await res.json();
        this.showMessage(data.message, !res.ok);
        if (res.ok) this.fetchApplications();
    },
    async handleFileUpload(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append('resume', file);
      const res = await fetch('http://localhost:5000/api/student/profile/resume', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: formData
      });
      if (res.ok) {
          this.showMessage("Resume uploaded!", false);
          this.fetchProfile();
      }
    },
    async fetchApplications() {
        const res = await fetch('http://localhost:5000/api/student/applications', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (res.ok) this.applications = await res.json();
    },
    
    // FIXED: Now checks drive_id against the application history
    isAlreadyApplied(driveId) {
        return this.applications.some(app => app.drive_id === driveId);
    },

    statusClass(s) {
      if (s === 'Selected') return 'bg-success';
      if (s === 'Rejected') return 'bg-danger';
      return 'bg-primary';
    },
    showMessage(msg, isErr) {
      this.message = msg; this.isError = isErr;
      setTimeout(() => { this.message = ''; }, 4000);
    }
  },
  mounted() {
    this.fetchDrives();
    this.fetchApplications();
    this.fetchProfile();
  }
}
</script>
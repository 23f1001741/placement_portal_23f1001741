<template>
  <div>
    <nav class="navbar navbar-dark bg-secondary mb-4 shadow">
      <div class="container">
        <span class="navbar-brand mb-0 h1">Company Dashboard</span>
        <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
      </div>
    </nav>

    <div class="container pb-5">
      <div v-if="message" :class="['alert', isError ? 'alert-danger' : 'alert-success']" class="shadow-sm">
        {{ message }}
      </div>

      <div class="row mb-4">
        <div class="col-md-4">
          <div class="card shadow-sm border-info bg-light h-100">
            <div class="card-body">
              <h6 class="text-muted small text-uppercase font-weight-bold">Profile Status</h6>
              <h4 :class="companyStats.approval_status === 'Approved' ? 'text-success' : 'text-warning'">
                {{ companyStats.approval_status || 'Checking...' }}
              </h4>
              <p class="mb-0 mt-2 small text-muted"><strong>{{ companyStats.company_name }}</strong></p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card shadow-sm border-primary h-100">
            <div class="card-body text-center">
              <h6 class="text-muted small text-uppercase font-weight-bold">Total Drives</h6>
              <h2 class="display-6">{{ companyStats.total_drives }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card shadow-sm border-success h-100">
            <div class="card-body text-center">
              <h6 class="text-muted small text-uppercase font-weight-bold">Total Applicants</h6>
              <h2 class="display-6">{{ companyStats.total_applicants }}</h2>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-md-4 mb-4">
          <div class="card shadow-sm border-primary">
            <div class="card-header bg-primary text-white"><h5 class="mb-0">New Placement Drive</h5></div>
            <div class="card-body">
              <form @submit.prevent="createDrive">
                <div class="mb-2">
                  <label class="small fw-bold">Job Title</label>
                  <input type="text" class="form-control form-control-sm" v-model="newDrive.job_title" required>
                </div>
                <div class="mb-2">
                  <label class="small fw-bold">Description</label>
                  <textarea class="form-control form-control-sm" v-model="newDrive.job_description" rows="2" required></textarea>
                </div>
                <div class="mb-2">
                  <label class="small fw-bold">Min CGPA</label>
                  <input type="number" step="0.1" class="form-control form-control-sm" v-model="newDrive.minimum_cgpa" required>
                </div>
                <div class="mb-3">
                  <label class="small fw-bold">Deadline</label>
                  <input type="date" class="form-control form-control-sm" v-model="newDrive.application_deadline" required>
                </div>
                <button type="submit" class="btn btn-primary btn-sm w-100 shadow-sm" :disabled="companyStats.approval_status !== 'Approved'">
                  {{ companyStats.approval_status === 'Approved' ? 'Submit Drive' : 'Awaiting Admin Approval' }}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div class="col-md-8">
          <h4 class="mb-3 border-bottom pb-2">Active Drives</h4>
          <div v-if="drives.length === 0" class="alert alert-info py-2 small">No drives created yet.</div>
          
          <div v-else class="table-responsive mb-4">
            <table class="table table-sm table-hover align-middle bg-white shadow-sm border">
              <thead class="table-dark">
                <tr><th>Role</th><th>Deadline</th><th>Status</th><th>Actions</th></tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id">
                  <td class="fw-bold">{{ drive.job_title }}</td>
                  <td>{{ drive.deadline }}</td>
                  <td><span class="badge" :class="drive.status === 'Approved' ? 'bg-success' : 'bg-warning text-dark'">{{ drive.status }}</span></td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="viewApplicants(drive)">Applicants</button>
                      <button class="btn btn-outline-success" @click="requestExport(drive.id)">CSV</button>
                      <button v-if="drive.status === 'Approved'" class="btn btn-outline-danger" @click="closeDrive(drive.id)">Close</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="selectedDrive" class="card shadow-sm border-info">
            <div class="card-header bg-info text-white d-flex justify-content-between align-items-center py-2">
              <h6 class="mb-0">Applicants for {{ selectedDrive.job_title }}</h6>
              <button class="btn btn-close btn-close-white" @click="selectedDrive = null"></button>
            </div>
            <div class="card-body p-0">
              <div v-if="applicants.length === 0" class="p-3 text-muted small">No applications found.</div>
              <div v-else class="table-responsive">
                <table class="table table-sm table-striped mb-0 align-middle">
                  <thead>
                    <tr class="small"><th>Student</th><th>Set Status</th><th>Interview</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="student in applicants" :key="student.id">
                      <td class="ps-3">
                        <div class="small fw-bold">{{ student.student_name }}</div>
                        <a v-if="student.resume_url" 
                           :href="'http://localhost:5000/uploads/resumes/' + student.resume_url" 
                           target="_blank" 
                           class="text-decoration-none small text-primary">
                           📄 View Resume
                        </a>
                        <span v-else class="small text-muted italic">No Resume</span>
                      </td>
                      <td>
                        <select v-model="student.status" @change="updateApplicationStatus(student.id, student.status)" class="form-select form-select-sm py-0" style="font-size: 0.75rem;">
                          <option value="Applied">Applied</option>
                          <option value="Shortlisted">Shortlisted</option>
                          <option value="Interview Scheduled">Interview</option>
                          <option value="Selected">Selected</option>
                          <option value="Rejected">Rejected</option>
                        </select>
                      </td>
                      <td>
                        <div v-if="student.status === 'Interview Scheduled'" class="input-group input-group-sm">
                          <input type="datetime-local" class="form-control py-0" style="font-size: 0.7rem;" v-model="student.interview_date">
                          <button class="btn btn-primary btn-xs" @click="scheduleInterview(student)">Set</button>
                        </div>
                        <span v-else-if="student.interview_date" class="small text-muted">{{ student.interview_date.replace('T', ' ') }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
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
      companyStats: { total_drives: 0, total_applicants: 0, approval_status: '', company_name: '' },
      drives: [],
      newDrive: { job_title: '', job_description: '', eligibility_criteria: '', minimum_cgpa: 0, application_deadline: '' },
      message: '',
      isError: false,
      selectedDrive: null,
      applicants: []
    }
  },
  methods: {
    logout() { localStorage.clear(); this.$router.push('/login'); },
    async fetchStats() {
      const res = await fetch('http://localhost:5000/api/company/stats', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) this.companyStats = await res.json();
    },
    async fetchDrives() {
      const res = await fetch('http://localhost:5000/api/company/drives', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) {
        this.drives = await res.json();
        this.fetchStats();
      }
    },
    async createDrive() {
      const res = await fetch('http://localhost:5000/api/company/drives', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(this.newDrive)
      });
      const data = await res.json();
      this.showMessage(data.message, !res.ok);
      if (res.ok) {
          this.newDrive = { job_title: '', job_description: '', minimum_cgpa: 0, application_deadline: '' };
          this.fetchDrives();
      }
    },
    async viewApplicants(drive) {
      this.selectedDrive = drive;
      const res = await fetch(`http://localhost:5000/api/company/drives/${drive.id}/applications`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) this.applicants = await res.json();
    },
    async updateApplicationStatus(id, status) {
      await fetch(`http://localhost:5000/api/company/applications/${id}/status`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      this.fetchStats();
    },
    async scheduleInterview(student) {
      const res = await fetch(`http://localhost:5000/api/company/applications/${student.id}/schedule`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: student.interview_date })
      });
      if (res.ok) this.showMessage("Interview scheduled!", false);
    },
    async requestExport(id) {
      const res = await fetch(`http://localhost:5000/api/company/drives/${id}/export`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await res.json();
      this.showMessage(data.message, !res.ok);
    },
    async closeDrive(id) {
       if(!confirm("Close drive?")) return;
       await fetch(`http://localhost:5000/api/company/drives/${id}/close`, {
         method: 'POST',
         headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
       });
       this.fetchDrives();
    },
    showMessage(msg, isErr) {
      this.message = msg; this.isError = isErr;
      setTimeout(() => { this.message = ''; }, 4000);
    }
  },
  mounted() {
    this.fetchDrives();
  }
}
</script>
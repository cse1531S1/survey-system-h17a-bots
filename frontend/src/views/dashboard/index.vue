<template>
  <div class="dashboard-container">
    <component :is="currentRole"></component>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import adminDashboard from './admin/index'
import staffDashboard from './staff/index'
import studentDashboard from './student/index'

export default {
  name: 'dashboard',
  components: { adminDashboard, studentDashboard, staffDashboard },
  data() {
    return {
      currentRole: 'adminDashboard'
    }
  },
  computed: {
    ...mapGetters([
      'roles'
    ])
  },
  created() {
    if (this.roles.indexOf('admin') >= 0) {
      return
    }
    if (this.roles.indexOf('staff') >= 0) {
      this.currentRole = 'staffDashboard'
      return
    }
    this.currentRole = 'studentDashboard'
  }
}
</script>

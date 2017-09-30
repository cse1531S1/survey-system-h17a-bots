<template>
  <div class="dashboard-container">
    <component :is="currentRole"></component>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import adminSurveyBoard from './admin/index'
import staffSurveyBoard from './staff/index'
import studentSurveyBoard from './student/index'

export default {
  name: 'dashboard',
  components: { adminSurveyBoard, studentSurveyBoard, staffSurveyBoard },
  data() {
    return {
      currentRole: 'adminSurveyBoard'
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
      this.currentRole = 'staffSurveyBoard'
      return
    }
    this.currentRole = 'studentSurveyBoard'
  }
}
</script>

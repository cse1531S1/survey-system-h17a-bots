<template>
  <div class="dashboard-editor-container">
    <el-row type="flex" justify="center">
      <el-col :span="6">
        <el-card class="box-card">
          <div slot="header" class="box-card-header">
            <pan-thumb class="panThumb" :name="name"> You are:
              <span class="pan-info-roles" :key='item' v-for="item in roles">{{item}}</span>
            </pan-thumb>
          </div>
          <span class="display_name">{{name}}</span>

          <div class="row">
            <div class="info-item">
              <count-to class="info-item-num" :startVal='0' :endVal='statisticsData.survey_count' :duration='3400'></count-to>
              <span class="info-item-text">Surveys</span>
              <icon-svg icon-class="a" class="dashboard-editor-icon"></icon-svg>
            </div>
            <div class="info-item">
              <count-to class="info-item-num" :startVal='0' :endVal='statisticsData.response_count' :duration='3600'></count-to>
              <span class="info-item-text">Response</span>
              <icon-svg icon-class="b" class="dashboard-editor-icon"></icon-svg>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- <el-col :span="8">
        <pie-chart></pie-chart>
      </el-col>

      <el-col :span="10">
        <bar-chart></bar-chart>
      </el-col> -->

    </el-row>

    <!-- <el-row :gutter="20">
      <line-chart></line-chart>
    </el-row> -->

  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import countTo from 'vue-count-to'
import panThumb from '@/components/PanThumb'
import pieChart from './pieChart'
import barChart from './barChart'
import lineChart from './lineChart'
import { fetchSRstatic } from '@/api/article'

export default {
  name: 'dashboard-admin',
  components: { countTo, panThumb, pieChart, lineChart, barChart },
  data() {
    return {
      statisticsData: {
        survey_count: 0,
        response_count: 0
      }
    }
  },
  created() {
    this.getData()
  },
  computed: {
    ...mapGetters([
      'name',
      'avatar',
      'roles'
    ])
  },
  methods: {
    getData() {
      fetchSRstatic().then(response => {
        this.statisticsData.survey_count = response.data.surveys
        this.statisticsData.response_count = response.data.responses
      })
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
.dashboard-editor-container {
  margin: 30px;
  .btn-group {
    margin-bottom: 60px;
  }
  .box-card-header {
    position: relative;
    height: 160px;
  }
  .panThumb {
    z-index: 100;
    height: 150px;
    width: 150px;
    position: absolute;
    left: 0px;
    right: 0px;
    margin: auto;
  }
  .display_name {
    text-align: center;
    font-size: 30px;
    display: block;
  }
  .info-item {
    display: inline-block;
    margin-top: 10px;
    font-size: 14px; // &:last-of-type {
    // margin-left: 15px;
    // }
  }
  .row {
    text-align: center;
  }
}
</style>

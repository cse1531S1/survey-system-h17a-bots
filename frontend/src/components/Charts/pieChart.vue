<template>
  <div :class="className" :style="{height:height,width:width}">
  </div>
</template>

<script>
import echarts from 'echarts'
import { fetchPie } from '@/api/article'
require('echarts/theme/macarons') // echarts 主题

export default {
  props: {
    className: {
      type: String,
      default: 'chart'
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '300px'
    },
    questionId: {
      type: Number
    },
    surveyId: {
      type: String
    }
  },
  data() {
    return {
      title: '',
      legend: [],
      data: [],
      chart: null
    }
  },
  created() {
    this.fetchPie(this.surveyId, this.questionId)
  },
  beforeDestroy() {
    if (!this.chart) {
      return
    }
    this.chart.dispose()
    this.chart = null
  },
  methods: {
    fetchPie(surveyId, questionId) {
      fetchPie(surveyId, questionId).then(response => {
        if (response.data.success) {
          this.legend = response.data.legend
          this.data = response.data.data
          this.title = response.data.title
        }
      }).then(() => {
        this.initChart()
      })
    },
    initChart() {
      this.chart = echarts.init(this.$el, 'macarons')

      this.chart.setOption({
        title: {
          text: this.title,
          x: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c} ({d}%)'
        },
        legend: {
          x: 'center',
          y: 'bottom',
          data: this.legend
        },
        calculable: true,
        series: [
          {
            name: this.title,
            type: 'pie',
            roseType: 'radius',
            data: this.data,
            animationEasing: 'cubicInOut',
            animationDuration: 2600
          }
        ]
      })
    }
  }
}
</script>

<template>
  <div class="app-container calendar-list-container">
    <div class="filter-container">
      <el-button class="filter-item" type="primary" v-waves icon="view" @click="handleShowPie">Statistic</el-button>
      <a v-if="success_load" class="el-button el-button--primary filter-item" type="primary" v-waves icon="document" :href="'download/'+surveyId+'.csv'"><i class="el-icon-document"></i> Download csv</a>
    </div>

    <el-table :key='tableKey' :data="list" v-loading="listLoading" element-loading-text="Loading!!!!" border fit highlight-current-row style="width: 100%">

      <!-- <el-table-column align="center" width="100px" label="User">
        <template scope="scope">
          <span>{{scope.row.name}}</span>
        </template>
      </el-table-column> -->

      <el-table-column width="100px" align="center" label="Time">
        <template scope="scope">
          <span>{{scope.row.time}}</span>
        </template>
      </el-table-column>

      <el-table-column min-width="350px" label="Response">
        <template scope="scope">
          <el-row v-for="answer in scope.row.answers" :key="answer.question">{{answer.question}}: {{answer.answer}}</el-row>
        </template>
      </el-table-column>
    </el-table>

    <div v-show="!listLoading" class="pagination-container">
      <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page.sync="listQuery.page" :page-sizes="[10,20,30,50]" :page-size="listQuery.limit" layout="total, sizes, prev, pager, next, jumper" :total="total">
      </el-pagination>
    </div>

    <el-dialog title="Statistical Report" :visible.sync="pieDialog" size="large">
      <div v-for="i in questions" :key="i">
        <pie-chart :surveyId="surveyId" :questionId="i"></pie-chart>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { fetchAnswers } from '@/api/article'
import waves from '@/directive/waves.js'// 水波纹指令
import pieChart from '@/components/Charts/pieChart.vue'
import { parseTime } from '@/utils'

export default {
  name: 'SurveyList',
  directives: {
    waves
  },
  components: {
    pieChart
  },
  data() {
    return {
      success_load: false,
      list: null,
      total: null,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        title: undefined,
        sort: '+id'
      },
      pieDialog: false,
      questions: [],
      tableKey: 0,
      surveyId: 0
    }
  },
  filters: {
  },
  created() {
    this.getList()
    this.listLoading = false
    this.surveyId = this.$route.params.id
  },
  methods: {
    handleShowPie() {
      this.pieDialog = true
    },
    getList() {
      this.listLoading = true
      fetchAnswers(this.listQuery, this.$route.params.id).then(response => {
        if (response.data.success) {
          this.list = response.data.items
          this.questions = response.data.questions
          this.total = response.data.total
          this.success_load = true
        } else {
          this.$message({
            message: response.data.message,
            type: 'error',
            duration: 6000
          })
        }
      }).then(() => {
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleSizeChange(val) {
      this.listQuery.limit = val
      this.getList()
    },
    handleCurrentChange(val) {
      this.listQuery.page = val
      this.getList()
    },
    formatJson(filterVal, jsonData) {
      return jsonData.map(v => filterVal.map(j => {
        if (j === 'timestamp') {
          return parseTime(v[j])
        } else {
          return v[j]
        }
      }))
    }
  }
}
</script>


<style scoped>
.list-complete-item {
  cursor: pointer;
  position: relative;
  font-size: 14px;
  padding: 5px 12px;
  margin-top: 4px;
  border: 1px solid #bfcbd9;
  transition: all 1s;
}

.list-complete-item.sortable-chosen {
  background: #4AB7BD;
}

.list-complete-item.sortable-ghost {
  background: #30B08F;
}
</style>

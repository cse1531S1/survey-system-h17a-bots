<template>
  <div class="app-container calendar-list-container">
    <div class="filter-container">
      <el-input @keyup.enter.native="handleFilter" style="width: 200px;" class="filter-item" placeholder="Username..." v-model="listQuery.title"></el-input>

      <el-button class="filter-item" type="primary" v-waves icon="search" @click="handleFilter">Search</el-button>
    </div>

    <el-table :key='tableKey' :data="list" v-loading="listLoading" element-loading-text="Loading..." border fit highlight-current-row style="width: 100%">

      <el-table-column min-width="150px" label="Username">
        <template scope="scope">
          <span class="">{{scope.row.name}}</span>
        </template>
      </el-table-column>

      <el-table-column width="250px" align="center" label="Courses">
        <template scope="scope">
          <el-row v-for="course in scope.row.courses" :key="course">{{course}}</el-row>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="Status" width="90">
        <template scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{scope.row.status}}</el-tag>
        </template>
      </el-table-column>

      <el-table-column align="center" label="Operation" width="150px">
        <template scope="scope">
          <el-button v-waves v-if="scope.row.status==='verified'" size="small" type="danger" @click="handleModifyStatus(scope.row,'unverified')">Forbid</el-button>
          <el-button v-waves v-if="scope.row.status==='unverified'" size="small" type="success" @click="handleModifyStatus(scope.row,'verified')">Verify</el-button>
        </template>
      </el-table-column>

    </el-table>

    <div v-show="!listLoading" class="pagination-container">
      <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page.sync="listQuery.page" :page-sizes="[10,20,30,50]" :page-size="listQuery.limit" layout="total, sizes, prev, pager, next, jumper" :total="total">
      </el-pagination>
    </div>
  </div>
</template>

<script>
import { fetchUnverified, modifyUser } from '@/api/article'
import draggable from 'vuedraggable'
import waves from '@/directive/waves.js'// 水波纹指令
import { parseTime } from '@/utils'

export default {
  name: 'SurveyList',
  directives: {
    waves
  },
  components: {
    draggable
  },
  data() {
    return {
      showWarning: false,
      list: null,
      total: null,
      listLoading: true,
      course: [],
      listQuery: {
        page: 1,
        limit: 20,
        title: undefined,
        sort: '+id'
      },
      importanceOptions: [1, 2, 3],
      sortOptions: [{ label: 'Ascending by id', key: '+id' }, { label: 'Descending by id', key: '-id' }],
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      dialogPvVisible: false,
      tableKey: 0,
      temp: {},
      newQuestion: {
        title: '',
        qType: '',
        qOptional: false,
        choices: ['Very Strongly Agree', 'Strongly Agree', 'Agree', 'Disagree', 'Strongly Disagree', 'Very Strongly Disagree']
      }
    }
  },
  filters: {
    statusFilter(status) {
      const statusMap = {
        verified: 'success',
        unverified: 'danger'
      }
      return statusMap[status]
    }
  },
  created() {
    this.getList()
  },
  methods: {
    handleClean() {
      this.$refs['newQuestion'].resetFields()
      this.dialogQuestion = false
    },
    addNewChoice() {
      this.newQuestion.choices.push('')
    },
    deleteEle(ele) {
      for (const item of this.newQuestion.choices) {
        if (item === ele) {
          const index = this.newQuestion.choices.indexOf(item)
          this.newQuestion.choices.splice(index, 1)
          break
        }
      }
    },
    getList() {
      this.listLoading = true
      fetchUnverified(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
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
    handleModifyStatus(row, status) {
      row.status = status
      this.temp = Object.assign({}, row)
      this.update()
    },
    update() {
      modifyUser(this.temp).then((response) => {
        if (response.data.success) {
          this.$notify({
            title: 'Success!',
            message: 'You successfully updated the user status!',
            type: 'success',
            duration: 2000
          })
        } else {
          this.$notify({
            title: 'Failed!',
            message: 'An unknown error occured.',
            type: 'error',
            duration: 2000
          })
        }
      })
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
  background: #4ab7bd;
}

.list-complete-item.sortable-ghost {
  background: #30b08f;
}
</style>

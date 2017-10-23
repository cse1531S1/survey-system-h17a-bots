<template>
  <div class="app-container calendar-list-container">
    <div class="filter-container">
      <el-input @keyup.enter.native="handleFilter" style="width: 200px;" class="filter-item" placeholder="Title" v-model="listQuery.title">
      </el-input>

      <el-select @change='handleFilter' style="width: 120px" class="filter-item" v-model="listQuery.sort" placeholder="Sort">
        <el-option v-for="item in sortOptions" :key="item.key" :label="item.label" :value="item.key">
        </el-option>
      </el-select>
      <el-button class="filter-item" type="primary" v-waves icon="search" @click="handleFilter">Search</el-button>
    </div>

    <h5 class="">Surveys to review</h5>
    <el-table :key='tableKey' :data="list_open" v-loading="listLoading" element-loading-text="Loading!!!!" border fit highlight-current-row style="width: 100%">

      <el-table-column min-width="250px" label="Title">
        <template scope="scope">
          <span>{{scope.row.title}}</span>
        </template>
      </el-table-column>

      <el-table-column width="110px" align="center" label="Start Time">
        <template scope="scope">
          <span>{{parseTime(scope.row.start_time)}}</span>
        </template>
      </el-table-column>

      <el-table-column width="110px" align="center" label="End Time">
        <template scope="scope">
          <span>{{parseTime(scope.row.end_time)}}</span>
        </template>
      </el-table-column>

      <el-table-column width="110px" align="center" label="Course">
        <template scope="scope">
          <span>{{scope.row.course}}</span>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="Status" width="90">
        <template scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{scope.row.status}}</el-tag>
        </template>
      </el-table-column>

      <el-table-column width="110px" align="center" label="Links">
        <template scope="scope">
          <router-link v-if="scope.row.status === 'closed'" v-waves class="el-button el-button--small" :to="'/result/'+scope.row.id">Result</router-link>
          <el-button v-waves v-if="scope.row.status === 'review'" size="small" @click="handleReview(scope.row)">Review</el-button>
        </template>
      </el-table-column>

    </el-table>

    <h5 class="">Survey Results</h5>
    <el-table :key='tableKey2' :data="list_closed" v-loading="listLoading" element-loading-text="Loading!!!!" border fit highlight-current-row style="width: 100%">

      <el-table-column min-width="250px" label="Title">
        <template scope="scope">
          <span>{{scope.row.title}}</span>
        </template>
      </el-table-column>

      <el-table-column width="110px" align="center" label="Course">
        <template scope="scope">
          <span>{{scope.row.course}}</span>
        </template>
      </el-table-column>

      <el-table-column width="110px" align="center" label="Links">
        <template scope="scope">
          <router-link v-if="scope.row.status === 'closed'" v-waves class="el-button el-button--small" :to="'/result/'+scope.row.id">Result</router-link>
        </template>
      </el-table-column>

    </el-table>

    <div v-show="!listLoading" class="pagination-container">
      <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page.sync="listQuery.page" :page-sizes="[10,20,30,50]" :page-size="listQuery.limit" layout="total, sizes, prev, pager, next, jumper" :total="total">
      </el-pagination>
    </div>

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible" :close-on-click-modal="false">
      <el-row class="" type="flex" justify="center">
        <h5>Mandatory questions chosen by admin</h5>
      </el-row>
      <el-row class="" type="flex" justify="center" v-for="i in list3" :key="i.description">
        <el-row class="">{{ i.description }}: {{ i.type }}</el-row>
      </el-row>
      <br>
      <br>
      <br>
      <el-row class="" type="flex" justify="center">
        <el-form :rules="rules" class="large-space" :model="temp" label-position="left" label-width="70px" style='width: 800px; margin-left:50px;' ref="newSurvey">

          <div class="editor-container">
            <dnd-list :list1="list1" :list2="list2" list1Title="Chosen" list2Title="Optional Question Pool"></dnd-list>
          </div>
        </el-form>
      </el-row>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="review">Submit</el-button>
      </div>
    </el-dialog>
  </div>
</template>



<script>
import { fetchList, fetchQuestion, fetchCourse, modifySurvey } from '@/api/article'
import draggable from 'vuedraggable'
import DndList from '@/components/twoDndList'
import waves from '@/directive/waves.js'// 水波纹指令
import { parseTime } from '@/utils'

export default {
  name: 'SurveyList',
  directives: {
    waves
  },
  components: {
    draggable,
    DndList
  },
  data() {
    return {
      active: 0,
      list: null,
      list_open: [],
      list_closed: [],
      total: null,
      listLoading: true,
      course: [],
      options: {
        handle: '.drag-handler',
        animation: 150
      },
      listQuery: {
        page: 1,
        limit: 20,
        title: undefined,
        sort: '+id'
      },
      temp: {
        id: undefined,
        timestamp: 0,
        start_time: 0,
        end_time: 0,
        title: '',
        status: 'review',
        course: '',
        questions: []
      },
      importanceOptions: [1, 2, 3],
      sortOptions: [{ label: 'Ascending by id', key: '+id' }, { label: 'Descending by id', key: '-id' }],
      statusOptions: ['open', 'review', 'closed'],
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      qIdMap: {},
      list1: [],
      list2: [],
      list3: [],
      list4: [],
      dialogPvVisible: false,
      pvData: [],
      tableKey: 0,
      tableKey1: 1,
      tableKey2: 2,
      newQuestion: {
        title: '',
        qType: '',
        choices: ['Very Strongly Agree', 'Strongly Agree', 'Agree', 'Disagree', 'Strongly Disagree', 'Very Strongly Disagree']
      },
      qTypeAllowed: {
        1: 'Multiple Choices'
      },
      dialogQuestion: false,
      to_post: {},
      rules: {
        course: [
          { required: true, message: 'Please choose a course', trigger: 'change' }
        ],
        start_time: [
          { type: 'date', required: true, message: 'Please choose a start time', trigger: 'change' }
        ],
        end_time: [
          { type: 'date', required: true, message: 'Please choose a end time', trigger: 'change' }
        ],
        title: [
          { required: true, message: 'Please input a title', trigger: 'blur' }
        ]
      }
    }
  },
  filters: {
    statusFilter(status) {
      const statusMap = {
        open: 'success',
        review: 'gray',
        closed: 'danger'
      }
      return statusMap[status]
    },
    typeFilter(type) {
      return null
    }
  },
  created() {
    this.getList()
    this.getCourse()
  },
  methods: {
    filterList() {
      this.list_open = []
      this.list_closed = []
      for (let i = 0; i < this.list.length; i++) {
        if (this.list[i].status === 'review') this.list_open.push(this.list[i])
        if (this.list[i].status === 'closed') this.list_closed.push(this.list[i])
      }
    },
    checkformAndNext() {
      this.$refs['newSurvey'].validate((valid) => {
        if (valid) {
          this.active++
        } else {
          return false
        }
      })
    },
    next() {
      if (this.active++ > 2) this.active = 0
    },
    prev() {
      if (this.active-- < 0) this.active = 0
    },
    parseTime(time) {
      return parseTime(time)
    },
    getCourse() {
      fetchCourse(this.listQuery).then(response => {
        this.course = response.data.items
      })
    },
    getList() {
      this.listLoading = true
      fetchList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
      }).then(() => {
        this.filterList()
        this.listLoading = false
      })
      fetchQuestion().then(response => {
        this.list2 = response.data.optional
        this.questions_man = response.data.mandatory
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
    timeFilter(time) {
      if (!time[0]) {
        this.listQuery.start = undefined
        this.listQuery.end = undefined
        return
      }
      this.listQuery.start = parseInt(+time[0] / 1000)
      this.listQuery.end = parseInt((+time[1] + 3600 * 1000 * 24) / 1000)
    },
    handleReview(row) {
      this.resetTemp()
      this.listLoading = true
      this.temp = Object.assign({}, row)
      this.list1 = row.questions_opt
      this.list3 = row.questions_man
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.listLoading = false
    },
    review() {
      this.dialogFormVisible = false
      this.to_post = {
        'title': this.temp.title,
        'purpose': 'review',
        'course': this.temp.course,
        'questions_opt': this.list1,
        'questions_man': this.list3,
        'start': this.temp.start_time,
        'end': this.temp.end_time,
        'status': 'open',
        'id': this.temp.id
      }
      modifySurvey(this.to_post).then(response => {
        if (response.data.success) {
          this.$notify({
            title: 'Success!',
            message: 'You successfully updated the survey!',
            type: 'success',
            duration: 2000
          })
        } else {
          this.$notify({
            title: 'Not Success!',
            message: 'Some unknown error happened',
            type: 'error',
            duration: 2000
          })
        }
      }).then(() => {
        this.getList()
        this.resetTemp()
      })
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        timestamp: 0,
        title: '',
        status: 'open',
        questions: [],
        course: '',
        end_time: null,
        start_time: null
      }
      this.list1 = []
      this.list3 = []
      this.to_post = {}
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

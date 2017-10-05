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
      <el-button class="filter-item" style="margin-left: 10px;" @click="handleCreate" type="primary" icon="edit">Add a Survey</el-button>
      <el-button class="filter-item" type="primary" icon="document" @click="loadUsers">Load Users</el-button>
      <el-button class="filter-item" type="primary" icon="document" @click="handleDownload">Export</el-button>
    </div>

    <el-table :key='tableKey' :data="list" v-loading="listLoading" element-loading-text="Loading!!!!" border fit highlight-current-row style="width: 100%">

      <el-table-column align="center" label="ID" width="55" prop="id">
        <template scope="scope">
          <span>{{scope.row.id}}</span>
        </template>
      </el-table-column>

      <el-table-column width="150px" align="center" label="Creation time">
        <template scope="scope">
          <span>{{scope.row.timestamp}}</span>
        </template>
      </el-table-column>

      <el-table-column min-width="250px" label="Title">
        <template scope="scope">
          <span class="link-type" @click="handleUpdate(scope.row)">{{scope.row.title}}</span>
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

      <el-table-column width="110px" align="center" label="Owner">
        <template scope="scope">
          <span>{{scope.row.owner}}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="Responses" width="110">
        <template scope="scope">
          <span>{{scope.row.responses}}</span>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="Status" width="90">
        <template scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{scope.row.status}}</el-tag>
        </template>
      </el-table-column>

      <el-table-column align="center" label="Operation" width="180">
        <template scope="scope">
          <el-button v-waves v-if="scope.row.status!='open'" size="small" type="success" @click="handleModifyStatus(scope.row,'open')">Open
          </el-button>
          <el-button v-waves v-if="scope.row.status!='draft'" size="small" @click="handleModifyStatus(scope.row,'draft')">Draft
          </el-button>
          <el-button v-waves v-if="scope.row.status!='closed'" size="small" type="danger" @click="handleModifyStatus(scope.row,'closed')">Close
          </el-button>
        </template>
      </el-table-column>

      <el-table-column width="110px" align="center" label="Links">
        <template scope="scope">
          <router-link v-waves class="el-button el-button--small" :to="'/result/'+scope.row.id">Result</router-link>
        </template>
      </el-table-column>

    </el-table>

    <div v-show="!listLoading" class="pagination-container">
      <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page.sync="listQuery.page" :page-sizes="[10,20,30,50]" :page-size="listQuery.limit" layout="total, sizes, prev, pager, next, jumper" :total="total">
      </el-pagination>
    </div>

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible" :close-on-click-modal="false">
      <el-row class="" type="flex" justify="center">
        <el-form :rules="rules" class="large-space" :model="temp" label-position="left" label-width="70px" style='width: 800px; margin-left:50px;' ref="newSurvey">
          <el-steps :active="active" finish-status="success">
            <el-step title="General Info"></el-step>
            <el-step title="Choose Generic Questions"></el-step>
            <el-step title="Choose Optional Questions"></el-step>
          </el-steps>

          <template v-if="active == 0">

            <el-form-item label="Status">
              <el-select class="filter-item" v-model="temp.status" placeholder="Choose...">
                <el-option v-for="item in  statusOptions" :key="item" :label="item" :value="item">
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="Courses" prop="course">
              <el-select class="filter-item" v-model="temp.course" filterable placeholder="Choose...">
                <el-option v-for="item in  this.course" :key="item" :label="item" :value="item">
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="Start Time" prop="start_time">
              <el-date-picker v-model="temp.start_time" type="datetime" placeholder="Choose Start Time" format="dd-MM-yyyy HH:mm">
              </el-date-picker>
            </el-form-item>

            <el-form-item label="End Time" prop="end_time">
              <el-date-picker v-model="temp.end_time" type="datetime" placeholder="Choose End Time" format="dd-MM-yyyy HH:mm">
              </el-date-picker>
            </el-form-item>

            <el-form-item label="Title" prop="title">
              <el-input v-model="temp.title"></el-input>
            </el-form-item>
          </template>

          <template v-if="active == 1">
            <el-button class="filter-item" style="margin-left: 10px;" @click="handleCQuestion" type="primary" icon="edit">Add a question</el-button>

            <div class="editor-container">
              <dnd-list :list1="list1" :list2="list2" list1Title="Chosen" list2Title="Question Pool"></dnd-list>
            </div>
          </template>

        </el-form>
      </el-row>
      <div slot="footer" class="dialog-footer">
        <el-button style="margin-top: 12px;" @click="prev" v-if="active != 0">Previous</el-button>
        <el-button style="margin-top: 12px;" @click="next" v-if="active != 2 && active != 0">Next</el-button>
        <el-button style="margin-top: 12px;" @click="checkformAndNext" v-if="active == 0">Next</el-button>
        <!-- <el-button @click="handleClean" v-if="active == 2">Cancel</el-button> -->
        <el-button v-if="dialogStatus=='create' && active == 2" type="primary" @click="create">Submit</el-button>
        <el-button v-else-if="active == 2" type="primary" @click="update">Submit</el-button>
      </div>
    </el-dialog>

    <el-dialog title="Create Question" :visible.sync="dialogQuestion" size="small">
      <el-form class="large-space" :model="newQuestion" label-position="left" label-width="70px" style='width: 400px; margin-left:50px;'>
        <el-form-item label="Title">
          <el-input v-model="newQuestion.title"></el-input>
        </el-form-item>

        <el-form-item label="Question Type">
          <el-select class="filter-item" v-model="newQuestion.qType" placeholder="Choose...">
            <el-option v-for="(item, index) in  qTypeAllowed" :key="index" :label="item" :value="index">
            </el-option>
          </el-select>
          <div v-if="newQuestion.qType === '1'">
            <el-button @click="addNewChoice">Add a Choice</el-button>
            <draggable :list="newQuestion.choices" :options="{ handle: '.handler', draggable: '.list-complete-item'}">
              <el-row class="list-complete-item " v-for="(element,index) in newQuestion.choices" :key='index'>
                <el-col :span="2" class="handler">
                  <icon-svg icon-class="tuozhuai"></icon-svg>
                </el-col>
                <el-col :span="2">
                  <span style="" @click="deleteEle(element)">
                    <i style="color:#ff4949" class="el-icon-delete"></i>
                  </span>
                </el-col>
                <el-col :span="20">
                  <el-input class="list-complete-item-handle" v-model.lazy="newQuestion.choices[index]"></el-input>
                </el-col>
              </el-row>
            </draggable>
          </div>
        </el-form-item>

      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogQuestion= false">Cancel</el-button>
        <el-button type="primary" @click="createQuestion">Submit</el-button>
      </div>
    </el-dialog>
  </div>
</template>



<script>
import { fetchList, fetchQuestion, fetchCourse, modifySurvey, createSurvey, createQuestion, loadUsers } from '@/api/article'
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
      total: null,
      purpose: '',
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
        status: 'draft',
        course: '',
        questions: []
      },
      importanceOptions: [1, 2, 3],
      sortOptions: [{ label: 'Ascending by id', key: '+id' }, { label: 'Descending by id', key: '-id' }],
      statusOptions: ['open', 'draft', 'closed'],
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      qIdMap: {},
      list1: [],
      list2: [],
      dialogPvVisible: false,
      pvData: [],
      tableKey: 0,
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
        draft: 'gray',
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
    loadUsers() {
      this.listLoading = true
      loadUsers().then(response => {
        if (response.data.success) {
          this.$notify({
            title: 'Success!',
            message: 'You successfully load all users',
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
        this.listLoading = false
      })
    },
    handleClean() {
      this.dialogFormVisible = false
      this.$refs['newSurvey'].resetFields()
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
        this.listLoading = false
      })
      fetchQuestion().then(response => {
        this.list2 = response.data
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
    handleModifyStatus(row, status) {
      row.status = status
      this.purpose = 'update_status'
      this.temp = Object.assign({}, row)
      this.update()
    },
    handleCreate() {
      this.resetTemp()
      this.purpose = 'create'
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
    },
    handleUpdate(row) {
      this.resetTemp()
      this.purpose = 'update'
      this.listLoading = true
      this.temp = Object.assign({}, row)
      this.list1 = row.questions
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.listLoading = false
    },
    handleCQuestion(row) {
      this.resetQuestionTemp()
      this.dialogQuestion = true
    },
    handleDelete(row) {
      this.$notify({
        title: '成功',
        message: '删除成功',
        type: 'success',
        duration: 2000
      })
      const index = this.list.indexOf(row)
      this.list.splice(index, 1)
    },
    createQuestion() {
      var detail = {
        title: this.newQuestion.title,
        qType: this.newQuestion.qType,
        choices: this.newQuestion.choices
      }
      createQuestion(detail).then(response => {
        if (response.data.success) {
          this.$notify({
            title: 'Success!',
            message: 'You successfully created a question!',
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
        this.resetQuestionTemp()
        this.dialogQuestion = false
      })
    },
    create() {
      this.$refs['newSurvey'].validate((valid) => {
        if (valid) {
          this.to_post = {
            'title': this.temp.title,
            'course': this.temp.course,
            'questions': this.list1,
            'start': this.temp.start_time,
            'end': this.temp.end_time,
            'status': this.temp.status,
            'id': -1
          }
          createSurvey(this.to_post).then(response => {
            if (response.data.success) {
              this.$notify({
                title: 'Success!',
                message: 'You successfully created the survey!',
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
            this.dialogFormVisible = false
          })
        } else {
          return false
        }
      })
    },
    update() {
      this.dialogFormVisible = false
      this.to_post = {
        'title': this.temp.title,
        'course': this.temp.course,
        'questions': this.list1,
        'start': this.temp.start_time,
        'end': this.temp.end_time,
        'status': this.temp.status,
        'purpose': this.purpose,
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
      this.to_post = {}
    },
    resetQuestionTemp() {
      this.newQuestion = {
        title: '',
        qType: '',
        choices: ['Very Strongly Agree', 'Strongly Agree', 'Agree', 'Disagree', 'Strongly Disagree', 'Very Strongly Disagree']
      }
    },
    handleDownload() {
      require.ensure([], () => {
        const { export_json_to_excel } = require('vendor/Export2Excel')
        const tHeader = ['时间', '地区', '类型', '标题', '重要性']
        const filterVal = ['timestamp', 'province', 'type', 'title', 'importance']
        const data = this.formatJson(filterVal, this.list)
        export_json_to_excel(tHeader, data, 'table数据')
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
  background: #4AB7BD;
}

.list-complete-item.sortable-ghost {
  background: #30B08F;
}
</style>

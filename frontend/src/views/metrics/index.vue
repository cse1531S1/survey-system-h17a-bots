<template>
  <div class="app-container calendar-list-container">
    <div class="filter-container">
      <el-input @keyup.enter.native="handleFilter" style="width: 200px;" class="filter-item" placeholder="Title" v-model="listQuery.title">
      </el-input>

      <el-button class="filter-item" type="primary" v-waves icon="search" @click="handleFilter">Search</el-button>
    </div>

    <el-table :key='tableKey' :data="list" v-loading="listLoading" element-loading-text="Loading!!!!" border fit highlight-current-row style="width: 100%">

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

      <el-table-column align="center" label="Responses" width="120">
        <template scope="scope">
          <span>{{scope.row.responses}}</span>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="Status" width="90">
        <template scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{scope.row.status}}</el-tag>
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
            <el-step title="Choose Mandatory Questions"></el-step>
            <el-step title="Choose Optional Questions"></el-step>
          </el-steps>

          <template v-if="active == 0">

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
              <dnd-list :list1="list1" :list2="list2" list1Title="Chosen" list2Title="Mandatory Question Pool"></dnd-list>
            </div>
          </template>

          <template v-if="active == 2">
            <el-button class="filter-item" style="margin-left: 10px;" @click="handleCQuestion" type="primary" icon="edit">Add a question</el-button>

            <div class="editor-container">
              <dnd-list :list1="list3" :list2="list4" list1Title="Chosen" list2Title="Optional Question Pool"></dnd-list>
            </div>
          </template>

        </el-form>
      </el-row>

      <div slot="footer" class="dialog-footer">
        <el-button style="margin-top: 12px;" @click="prev" v-if="active != 0">Previous</el-button>
        <el-button style="margin-top: 12px;" @click="next" v-if="active != 2 && active != 0 && list1.length > 0 ">Next</el-button>
        <el-button style="margin-top: 12px;" @click="openAlert" v-if="active != 2 && active != 0 && list1.length === 0 ">Next</el-button>
        <el-button style="margin-top: 12px;" @click="checkformAndNext" v-if="active == 0">Next</el-button>
        <el-button v-if="dialogStatus=='create' && active == 2" type="primary" @click="create">Submit</el-button>
        <el-button v-else-if="active == 2" type="primary" @click="update">Submit</el-button>
      </div>
    </el-dialog>

    <el-dialog title="Create Question" :visible.sync="dialogQuestion" size="small">
      <el-form class="large-space" :model="newQuestion" label-position="left" label-width="70px" style='width: 400px; margin-left:50px;' :rules="createQuestionRules" ref="newQuestion">
        <el-form-item label="Title" prop="title">
          <el-input v-model="newQuestion.title"></el-input>
        </el-form-item>

        <el-form-item label="Optional">
          <el-switch v-model="newQuestion.qOptional" on-color="#13ce66" off-color="#ff4949"></el-switch>
        </el-form-item>

        <el-form-item label="Question Type" prop="qType">
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
    var validateDate = (rule, value, callback) => {
      if (value === undefined || value === '') {
        callback(new Error('Please choose a date'))
      } else {
        callback()
      }
    }
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
      newQuestion: {
        title: '',
        qType: '',
        qOptional: false,
        choices: ['Very Strongly Agree', 'Strongly Agree', 'Agree', 'Disagree', 'Strongly Disagree', 'Very Strongly Disagree']
      },
      qTypeAllowed: {
        1: 'Multiple choice',
        2: 'Text based'
      },
      dialogQuestion: false,
      to_post: {},
      loaded: true,
      rules: {
        course: [
          { required: true, message: 'Please choose a course', trigger: 'change' }
        ],
        start_time: [
          { required: true, validator: validateDate, trigger: 'blur' }
        ],
        end_time: [
          { required: true, validator: validateDate, trigger: 'blur' }
        ],
        title: [
          { required: true, message: 'Please input a title', trigger: 'blur' }
        ]
      },
      createQuestionRules: {
        title: [
          { required: true, message: 'Please enter a title for the question', trigger: 'blur' }
        ],
        qType: [
          { required: true, message: 'Please Choose a type for the question', trigger: 'blur' }
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
    openAlert() {
      this.$message({
        message: 'You must choose at least one mandatory question',
        type: 'warning'
      })
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
    loadUsers() {
      this.listLoading = true
      loadUsers().then(response => {
        if (response.data.success) {
          this.$notify({
            title: 'Success!',
            message: 'You successfully loaded all users',
            type: 'success',
            duration: 2000
          })
        } else {
          this.$notify({
            title: 'Failed!',
            message: 'An unknown error occured',
            type: 'error',
            duration: 2000
          })
        }
      }).then(() => {
        this.loaded = true
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
        this.loaded = response.data.loaded
        this.list2 = response.data.mandatory
        this.list4 = response.data.optional
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
      this.list1 = row.questions_man
      this.list3 = row.questions_opt
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.listLoading = false
    },
    handleCQuestion(row) {
      this.resetQuestionTemp()
      this.dialogQuestion = true
    },
    createQuestion() {
      this.$refs['newQuestion'].validate((valid) => {
        if (valid) {
          if (this.newQuestion.qType === '1' && this.newQuestion.choices.length === 0) {
            this.$notify({
              title: 'Failed!',
              message: 'A MCQ question should have at least 1 choice',
              type: 'error',
              duration: 2000
            })
          } else {
            var detail = {
              title: this.newQuestion.title,
              qType: this.newQuestion.qType,
              optional: this.newQuestion.qOptional,
              choices: this.newQuestion.choices
            }
            createQuestion(detail).then(response => {
              if (response.data.success) {
                this.$notify({
                  title: 'Success!',
                  message: 'You have successfully created a question!',
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
            }).then(() => {
              this.getList()
              this.resetQuestionTemp()
              this.dialogQuestion = false
            })
          }
        } else {
          return false
        }
      })
    },
    create() {
      this.$refs['newSurvey'].validate((valid) => {
        if (valid) {
          this.to_post = {
            'title': this.temp.title,
            'course': this.temp.course,
            'questions_man': this.list1,
            'questions_opt': this.list3,
            'start': this.temp.start_time,
            'end': this.temp.end_time,
            'status': 'review',
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
                title: 'Failed!',
                message: 'An unknown error occured.',
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
        'questions_man': this.list1,
        'questions_opt': this.list3,
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
            title: 'Failed!',
            message: 'An unknown error occured.',
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
      this.getCourse()
      this.temp = {
        id: undefined,
        timestamp: 0,
        title: '',
        status: 'review',
        questions: [],
        course: '',
        end_time: null,
        start_time: null
      }
      this.active = 0
      this.list1 = []
      this.list3 = []
      this.to_post = {}
    },
    resetQuestionTemp() {
      this.newQuestion = {
        title: '',
        qType: '',
        qOptional: false,
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
  background: #4ab7bd;
}

.list-complete-item.sortable-ghost {
  background: #30b08f;
}
</style>

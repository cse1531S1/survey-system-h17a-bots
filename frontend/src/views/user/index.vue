<template>
  <div class="app-container calendar-list-container">
    <div class="filter-container">
      <el-input @keyup.enter.native="handleFilter" style="width: 200px;" class="filter-item" placeholder="Title" v-model="listQuery.title">
      </el-input>

      <el-button class="filter-item" type="primary" v-waves icon="search" @click="handleFilter">Search</el-button>
      <el-button class="filter-item" v-waves style="margin-left: 10px;" @click="handleCQuestion" type="primary" icon="edit">Add a question</el-button>
    </div>

    <el-table :key='tableKey' :data="list" v-loading="listLoading" element-loading-text="Loading..." border fit highlight-current-row style="width: 100%">

      <el-table-column min-width="250px" label="Title">
        <template scope="scope">
          <span class="link-type" @click="handleUpdate(scope.row)">{{scope.row.title}}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="Optional" width="100">
        <template scope="scope">
          <span v-if="scope.row.optional">
            <i class="el-icon-check"></i>
          </span>
          <span v-else>
            <i class="el-icon-close"></i>
          </span>
        </template>
      </el-table-column>

      <el-table-column width="250px" align="center" label="Choices">
        <template scope="scope">
          <template v-if="scope.row.type==='Multiple Choices'">
            <el-row v-for="choice in scope.row.choices" :key="choice">{{choice}}</el-row>
          </template>
        </template>
      </el-table-column>

      <el-table-column width="110px" align="center" label="Type">
        <template scope="scope">
          <span>{{scope.row.type}}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="Operation" width="120">
        <template scope="scope">
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">Delete
          </el-button>
          </el-button>
        </template>
      </el-table-column>

    </el-table>

    <div v-show="!listLoading" class="pagination-container">
      <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page.sync="listQuery.page" :page-sizes="[10,20,30,50]" :page-size="listQuery.limit" layout="total, sizes, prev, pager, next, jumper" :total="total">
      </el-pagination>
    </div>

    <el-dialog title="Create Question" :visible.sync="dialogQuestion" size="small">
      <el-form class="large-space" :model="newQuestion" :rules="rules" ref="newQuestion" label-position="left" label-width="70px" style='width: 400px; margin-left:50px;'>
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
        </el-form-item>

        <div v-if="newQuestion.qType === '1'">
          <el-button @click="addNewChoice">Add a Choice</el-button>
          <draggable :list="newQuestion.choices" :options="{ handle: '.handler', draggable: '.list-complete-item'}">
            <el-row class="list-complete-item " v-for="(element,index) in newQuestion.choices" :key='index'>
              <el-col :span="2" class="handler">
                <icon-svg style="margin-top: 10px" icon-class="tuozhuai"></icon-svg>
              </el-col>
              <el-col :span="2">
                <span style="" @click="deleteEle(element)">
                  <i style="color:#ff4949;margin-top: 10px" class="el-icon-delete"></i>
                </span>
              </el-col>
              <el-col :span="20">
                <el-input class="list-complete-item-handle" v-model.lazy="newQuestion.choices[index]"></el-input>
              </el-col>
            </el-row>
          </draggable>
        </div>

      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="handleClean">Cancel</el-button>
        <el-button type="primary" @click="createQuestion('newQuestion')">Submit</el-button>
      </div>
    </el-dialog>

    <el-dialog title="Are you sure you want to delete this question?" :visible.sync="showWarning" size="small">
      <el-button @click="showWarning = false">Cancel</el-button>
      <el-button type="danger" @click="deleteQuestion">Delete</el-button>
    </el-dialog>
  </div>
</template>

<script>
import { fetchPool, createQuestion, deleteQuestion } from '@/api/article'
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
      importanceOptions: [1, 2, 3],
      sortOptions: [{ label: 'Ascending by id', key: '+id' }, { label: 'Descending by id', key: '-id' }],
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      qIdMap: {},
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
      to_delete: 0,
      rules: {
        title: [
          { required: true, message: 'Please enter the question title', trigger: 'blur' }
        ],
        qType: [
          { required: true, message: 'Please choose the question type', trigger: 'blur' }
        ]
      }
    }
  },
  filters: {
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
      fetchPool(this.listQuery).then(response => {
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
    handleCQuestion(row) {
      this.listLoading = true
      this.resetTemp()
      this.dialogQuestion = true
      this.listLoading = false
    },
    handleDelete(row) {
      this.showWarning = true
      this.to_delete = row.id
    },
    deleteQuestion() {
      var id = this.to_delete
      this.showWarning = false
      deleteQuestion(id).then(response => {
        if (response.data.success) {
          this.$notify({
            title: 'Success',
            message: 'You have successfully deleted a question!',
            type: 'success',
            duration: 4000
          })
        } else {
          this.$notify({
            title: 'Error',
            message: response.data.error,
            type: 'error',
            duration: 4000
          })
        }
      }).then(() => {
        this.getList()
        this.to_delete = 0
        this.showWarning = false
      })
    },
    createQuestion() {
      this.$refs['newQuestion'].validate((valid) => {
        if (valid) {
          var detail = {
            title: this.newQuestion.title,
            qType: this.newQuestion.qType,
            choices: this.newQuestion.choices,
            optional: this.newQuestion.qOptional
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
            this.resetTemp()
            this.dialogQuestion = false
          })
        } else {
          return false
        }
      })
    },
    resetTemp() {
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
  background: #4AB7BD;
}

.list-complete-item.sortable-ghost {
  background: #30B08F;
}
</style>

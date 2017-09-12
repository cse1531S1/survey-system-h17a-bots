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
          <el-button v-if="scope.row.status!='published'" size="small" type="success" @click="handleModifyStatus(scope.row,'published')">Publish
          </el-button>
          <el-button v-if="scope.row.status!='draft'" size="small" @click="handleModifyStatus(scope.row,'draft')">Draft
          </el-button>
          <el-button v-if="scope.row.status!='deleted'" size="small" type="danger" @click="handleModifyStatus(scope.row,'deleted')">Delete
          </el-button>
        </template>
      </el-table-column>

    </el-table>

    <div v-show="!listLoading" class="pagination-container">
      <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page.sync="listQuery.page" :page-sizes="[10,20,30,50]" :page-size="listQuery.limit" layout="total, sizes, prev, pager, next, jumper" :total="total">
      </el-pagination>
    </div>

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form class="small-space" :model="temp" label-position="left" label-width="70px" style='width: 400px; margin-left:50px;'>

        <el-form-item label="Status">
          <el-select class="filter-item" v-model="temp.status" placeholder="Choose...">
            <el-option v-for="item in  statusOptions" :key="item" :label="item" :value="item">
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="Courses">
          <el-select class="filter-item" v-model="temp.course" placeholder="Choose...">
            <el-option v-for="item in  this.course" :key="item" :label="item" :value="item">
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="Start Time">
          <el-date-picker v-model="temp.start_time" type="datetime" placeholder="Choose Start Time" format="dd-MM-yyyy HH:mm">
          </el-date-picker>
        </el-form-item>

        <el-form-item label="End Time">
          <el-date-picker v-model="temp.end_time" type="datetime" placeholder="Choose End Time" format="dd-MM-yyyy HH:mm">
          </el-date-picker>
        </el-form-item>

        <el-form-item label="Title">
          <el-input v-model="temp.title"></el-input>
        </el-form-item>

        <div class="editor-container">
          <dnd-list :list1="list1" :list2="list2" list1Title="Chosen" list2Title="Question Pool"></dnd-list>
        </div>

      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button v-if="dialogStatus=='create'" type="primary" @click="create">Submit</el-button>
        <el-button v-else type="primary" @click="update">Submit</el-button>
      </div>
    </el-dialog>

    <el-dialog title="阅读数统计" :visible.sync="dialogPvVisible" size="small">
      <el-table :data="pvData" border fit highlight-current-row style="width: 100%">
        <el-table-column prop="key" label="渠道"> </el-table-column>
        <el-table-column prop="pv" label="pv"> </el-table-column>
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogPvVisible = false">确 定</el-button>
      </span>
    </el-dialog>

  </div>
</template>

<script>
import { fetchList, fetchPv, fetchQuestion, fetchCourse, modifySurvey, createSurvey } from '@/api/article'
import DndList from '@/components/twoDndList'
import waves from '@/directive/waves.js'// 水波纹指令
import { parseTime } from '@/utils'

export default {
  name: 'SurveyList',
  directives: {
    waves
  },
  components: {
    DndList
  },
  data() {
    return {
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
      temp: {
        id: undefined,
        timestamp: 0,
        start_time: 0,
        end_time: 0,
        title: '',
        status: 'published',
        course: '',
        questions: []
      },
      importanceOptions: [1, 2, 3],
      sortOptions: [{ label: 'Ascending by id', key: '+id' }, { label: 'Descending by id', key: '-id' }],
      statusOptions: ['published', 'draft', 'deleted'],
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
      to_post: {}
    }
  },
  filters: {
    statusFilter(status) {
      const statusMap = {
        published: 'success',
        draft: 'gray',
        deleted: 'danger'
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
      // this.$message({
      //   message: 'Success',
      //   type: 'success'
      // })
      row.status = status
      this.temp = Object.assign({}, row)
      this.update()
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
    },
    handleUpdate(row) {
      this.resetTemp()
      this.listLoading = true
      this.temp = Object.assign({}, row)
      this.list1 = row.questions
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.listLoading = false
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
    create() {
      this.dialogFormVisible = false
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
        status: 'published',
        questions: [],
        course: '',
        end_time: null,
        start_time: null
      }
      this.list1 = []
      this.to_post = {}
    },
    handleFetchPv(pv) {
      fetchPv(pv).then(response => {
        this.pvData = response.data.pvData
        this.dialogPvVisible = true
      })
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
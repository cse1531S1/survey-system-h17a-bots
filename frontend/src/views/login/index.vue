<template>
  <div class="login-container">
    <el-form class="card-box login-form" autoComplete="on" :model="loginForm" :rules="loginRules" ref="loginForm" label-position="left">
      <h3 class="title">Login</h3>

      <el-form-item prop="username">
        <span class="svg-container svg-container_login">
          <icon-svg icon-class="yonghuming" />
        </span>
        <el-input name="username" type="text" v-model="loginForm.username" autoComplete="on" placeholder="zid" />
      </el-form-item>

      <el-form-item prop="password">
        <span class="svg-container">
          <icon-svg icon-class="mima" />
        </span>
        <el-input name="password" :type="pwdType" @keyup.enter.native="handleLogin" v-model="loginForm.password" autoComplete="on" placeholder="Password" />
        <span class='show-pwd' @click='showPwd'>
          <icon-svg icon-class="yanjing" />
        </span>
      </el-form-item>

      <el-button type="primary" style="width:100%;margin-bottom:20px;" :loading="loading" @click.native.prevent="handleLogin">Login</el-button>

      <el-button style="width:100%;margin-bottom:30px;margin-left:0px;" @click="handleRegister">Register</el-button>

    </el-form>

    <el-dialog title="Register" :visible.sync="dialogVisible" size="tiny" :close-on-click-modal="false">

      <el-form :model="temp" :rules="newUserRule" ref="newUser">
        <el-form-item label="Username" prop="username">
          <el-input v-model="temp.username" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input type="password" v-model="temp.password" placeholder=""></el-input>
        </el-form-item>

        <el-form-item label="Courses">
          <el-select class="filter-item" v-model="temp.course" filterable multiple placeholder="Choose...">
            <el-option v-for="item in  this.course" :key="item" :label="item" :value="item">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="handleSubmit">Submit</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { isvalidUsername } from '@/utils/validate'
import { register } from '@/api/login'
import { fetchCourse } from '@/api/article'

export default {
  components: {},
  name: 'login',
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!isvalidUsername(value)) {
        callback(new Error('Incorrect username'))
      } else {
        callback()
      }
    }
    const validatePassword = (rule, value, callback) => {
      callback()
    }
    return {
      dialogVisible: false,
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }]
      },
      pwdType: 'password',
      loading: false,
      showDialog: false,
      formLabelWidth: '120px',
      temp: {
        username: '',
        password: '',
        course: []
      },
      course: [],
      newUserRule: {
        username: [
          { required: true, message: 'Please enter a username', trigger: 'blur' }
        ],
        password: [
          { required: true, message: 'Please enter a password', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    getList() {
      fetchCourse(this.listQuery).then(response => {
        this.course = response.data.items
      })
    },
    showPwd() {
      if (this.pwdType === 'password') {
        this.pwdType = ''
      } else {
        this.pwdType = 'password'
      }
    },
    handleRegister() {
      this.temp.username = ''
      this.temp.password = ''
      this.temp.course = []
      this.dialogVisible = true
    },
    handleSubmit() {
      this.$refs['newUser'].validate((valid) => {
        if (valid) {
          register(this.temp).then(response => {
            if (response.data.success) {
              this.$notify({
                title: 'Success!',
                message: 'You have successfully created a guest user. You still cannot login until admin veifies your registation',
                type: 'success',
                duration: 4000
              })
              this.dialogVisible = false
            } else {
              this.$notify({
                title: 'Failed!',
                message: response.data.message,
                type: 'error',
                duration: 4000
              })
            }
          })
        } else {
          return false
        }
      })
    },
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          this.$store.dispatch('LoginByUsername', this.loginForm).then(() => {
            this.loading = false
            this.$router.push({ path: '/' })
          }).catch((rejectMessage) => {
            this.$message({
              // message: 'Invaild credentials or your account is not verified',
              message: rejectMessage,
              type: 'error',
              duration: 0,
              showClose: true
            })
            this.loading = false
          })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    }
  },
  created() {
    this.getList()
  },
  destroyed() {
  }
}
</script>

<style rel="stylesheet/scss" lang="scss">
@import 'src/styles/mixin.scss';
$bg: #2d3a4b;
$dark_gray: #889aa4;
$light_gray: #eee;

.login-container {
  @include relative;
  height: 100vh;
  background-color: $bg;
  input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0px 1000px #293444 inset !important;
    -webkit-text-fill-color: #fff !important;
  }
  .card-box {
    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $light_gray;
      height: 47px;
    }
    .el-input {
      display: inline-block;
      height: 47px;
      width: 85%;
    }
    .el-form-item {
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(0, 0, 0, 0.1);
      border-radius: 5px;
      color: #454545;
    }
  }
  .tips {
    font-size: 14px;
    color: #fff;
    margin-bottom: 10px;
  }
  .svg-container {
    padding: 6px 5px 6px 15px;
    color: $dark_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
    &_login {
      font-size: 20px;
    }
  }
  .title {
    font-size: 26px;
    font-weight: 400;
    color: $light_gray;
    margin: 0px auto 40px auto;
    text-align: center;
    font-weight: bold;
  }
  .login-form {
    position: absolute;
    left: 0;
    right: 0;
    width: 400px;
    padding: 35px 35px 15px 35px;
    margin: 120px auto;
  }
  .show-pwd {
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: $dark_gray;
    cursor: pointer;
  }
}
</style>

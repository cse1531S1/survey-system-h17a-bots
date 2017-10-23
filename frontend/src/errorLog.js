import Vue from 'vue'
import errLog from '@/store/errLog'

if (process.env.NODE_ENV === 'production') {
  Vue.config.errorHandler = function(err, vm) {
    console.log(err, window.location.href)
    errLog.pushLog({
      err,
      url: window.location.href,
      vm
    })
  }
}

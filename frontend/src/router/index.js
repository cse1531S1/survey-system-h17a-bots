import Vue from 'vue'
import Router from 'vue-router'
const _import = require('./_import_' + process.env.NODE_ENV)
// in development env not use Lazy Loading,because Lazy Loading too many pages will cause webpack hot update too slow.so only in production use Lazy Loading

Vue.use(Router)

/* layout */
import Layout from '../views/layout/Layout'

/**
* icon : the icon show in the sidebar
* hidden : if `hidden:true` will not show in the sidebar
* redirect : if `redirect:noredirect` will no redirct in the levelbar
* noDropdown : if `noDropdown:true` will has no submenu
* meta : { role: ['admin'] }  will control the page role
**/
export const constantRouterMap = [
  { path: '/login', component: _import('login/index'), hidden: true },
  { path: '/authredirect', component: _import('login/authredirect'), hidden: true },
  { path: '/404', component: _import('errorPage/404'), hidden: true },
  { path: '/401', component: _import('errorPage/401'), hidden: true },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    icon: 'wujiaoxing',
    hidden: true,
    noDropdown: true,
    children: [{ path: 'dashboard', component: _import('dashboard/index'), name: 'Dashboard' }]
  }
]

export default new Router({
  // mode: 'history', //后端支持可开
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRouterMap
})

export const asyncRouterMap = [
  {
    path: '/survey',
    component: Layout,
    meta: { role: ['admin', 'student', 'staff'] },
    icon: 'wujiaoxing',
    noDropdown: true,
    children: [
      {
        path: 'index',
        component: _import('survey/index'),
        name: 'Survey Panel',
        meta: { role: ['admin', 'student', 'staff'] }
      }
    ]
  },
  {
    path: '/question',
    component: Layout,
    meta: { role: ['admin'] },
    icon: 'wujiaoxing',
    noDropdown: true,
    children: [
      {
        meta: { role: ['admin'] },
        path: 'questionpool',
        component: _import('question/index'),
        name: 'Question Pool'
      }
    ]
  },
  {
    path: '/result',
    hidden: true,
    component: Layout,
    meta: { role: ['admin', 'student', 'staff'] },
    children: [
      {
        meta: { role: ['admin', 'student', 'staff'] },
        path: '/result/:id',
        component: _import('result/index'),
        name: 'Survey Result'
      }
    ]
  },
  { path: '*', redirect: '/404', hidden: true }
]

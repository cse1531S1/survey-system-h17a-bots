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
    name: 'Dashboard',
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
    path: '/components',
    component: Layout,
    redirect: '/components/index',
    name: '组件',
    icon: 'zujian',
    children: [
      { path: 'index', component: _import('components/index'), name: '介绍 ' },
      { path: 'dndlist', component: _import('components/dndList'), name: '列表拖拽' },
      { path: 'dropzone', component: _import('components/dropzone'), name: 'Dropzone' }
    ]
  },
  {
    path: '/survey',
    component: Layout,
    redirect: '/survey/surveylist',
    name: 'Survey',
    icon: 'zujian',
    children: [
      { path: 'surveylist', component: _import('survey/surveylist'), name: 'SurveyList' },
      { path: 'createsurvey', component: _import('survey/createsurvey'), name: 'Create Survey' }
    ]
  },
  {
    path: '/question',
    component: Layout,
    redirect: '/question/questionpool',
    name: 'Question',
    icon: 'zujian',
    children: [
      { path: 'questionpool', component: _import('question/questionpool'), name: 'Question Pool' },
      { path: 'createquestion', component: _import('question/createquestion'), name: 'Create Question' }
    ]
  },
  {
    path: '/example',
    component: Layout,
    redirect: 'noredirect',
    name: '综合实例',
    icon: 'zonghe',
    children: [
      {
        path: '/example/table',
        component: _import('example/table/index'),
        redirect: '/example/table/table',
        name: 'Table',
        icon: 'table',
        children: [
          { path: 'dynamictable', component: _import('example/table/dynamictable/index'), name: '动态table' },
          { path: 'dragtable', component: _import('example/table/dragTable'), name: '拖拽table' },
          { path: 'inline_edit_table', component: _import('example/table/inlineEditTable'), name: 'table内编辑' },
          { path: 'table', component: _import('example/table/table'), name: '综合table' }
        ]
      },
      { path: 'form/edit', icon: 'shouce', component: _import('example/form'), name: '编辑Form', meta: { isEdit: true }},
      { path: 'form/create', icon: 'from', component: _import('example/form'), name: '创建Form' },
      { path: 'tab/index', icon: 'tab', component: _import('example/tab/index'), name: 'Tab' }
    ]
  },

  { path: '*', redirect: '/404', hidden: true }
]

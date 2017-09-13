<template>
  <div class="twoDndList">
    <div class="twoDndList-list" :style="{width:width1}">
      <h3>{{list1Title}}</h3>
      <draggable :list="list1" class="dragArea">
        <div class="list-complete-item" v-for="element in list1" :key='element'>
          <el-input class="list-complete-item-handle"></el-input>
          <div style="position:absolute;right:0px;">
            <span style="float: right ;margin-top: -35px;margin-right:-20px;" @click="deleteEle(element)">
              <i style="color:#ff4949" class="el-icon-delete"></i>
            </span>
          </div>
        </div>
      </draggable>
    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable'

export default {
  name: 'CreateQuestionForm',
  components: { draggable },
  computed: {
  },
  props: {
    list1: {
      type: Array,
      default() {
        return []
      }
    },
    list1Title: {
      type: String,
      default: 'list1'
    },
    width1: {
      type: String,
      default: '100%'
    }
  },
  methods: {
    deleteEle(ele) {
      for (const item of this.list1) {
        if (item.id === ele.id) {
          const index = this.list1.indexOf(item)
          this.list1.splice(index, 1)
          break
        }
      }
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
.twoDndList {
  background: #fff;
  padding-bottom: 40px;
  &:after {
    content: "";
    display: table;
    clear: both;
  }
  .twoDndList-list {
    float: left;
    padding-bottom: 30px;
    &:first-of-type {
      margin-right: 2%;
    }
    .dragArea {
      margin-top: 15px;
      min-height: 50px;
      padding-bottom: 30px;
    }
  }
}

.list-complete-item {
  cursor: pointer;
  position: relative;
  font-size: 14px;
  padding: 5px 12px;
  margin-top: 4px;
  border: 1px solid #bfcbd9;
  transition: all 1s;
}

.list-complete-item-handle {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 50px;
}

.list-complete-item.sortable-chosen {
  background: #4AB7BD;
}

.list-complete-item.sortable-ghost {
  background: #30B08F;
}

.list-complete-enter,
.list-complete-leave-active {
  opacity: 0;
}
</style>

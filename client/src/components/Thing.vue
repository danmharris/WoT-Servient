<template>
  <div>
    <span class="md-title">{{ this.td.title }}</span>
    <span class="md-body">{{ this.td.description }}</span>
    <span class="md-subheading">Actions</span>
    <md-table>
      <md-table-row>
        <md-table-head>Name</md-table-head>
        <md-table-head>Description</md-table-head>
        <md-table-head>Run</md-table-head>
      </md-table-row>
      <md-table-row v-for="(action, name) in this.td.actions" :key="name">
        <md-table-cell>{{ name }}</md-table-cell>
        <md-table-cell>{{ action.description }}</md-table-cell>
        <md-table-cell><md-button class="md-icon-button" @click="runAction(name)"><md-icon>play_circle_filled</md-icon></md-button></md-table-cell>
      </md-table-row>
    </md-table>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Thing',
  data() {
    return {
      td: {},
    }
  },
  methods: {
    runAction: async function(name) {
        await axios.post(this.td.base + this.td.actions[name].forms[0].href)
    }
  },
  async mounted() {
    const res = await axios.get(`${process.env.VUE_APP_API_BASE_URI}/directory/things/${this.$route.params.id}`)
    this.td = res.data
  }
}
</script>

<style scoped>
div > span {
    padding: 0.5em;
    display: inline-block;
}
div > .md-subheading {
    display: block;
}
</style>

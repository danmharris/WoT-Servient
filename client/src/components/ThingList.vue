<template>
  <md-table>
    <md-table-row>
      <md-table-head>Title</md-table-head>
      <md-table-head>Description</md-table-head>
      <md-table-head>View</md-table-head>
    </md-table-row>
    <md-table-row v-for="thing in things" :key="thing.id">
      <md-table-cell>{{ thing.title }}</md-table-cell>
      <md-table-cell>{{ thing.description || 'N/A' }}</md-table-cell>
      <md-table-cell><router-link :to="'/things/' + thing.id"><md-icon>launch</md-icon></router-link></md-table-cell>
    </md-table-row>
  </md-table>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ThingList',
  data() {
    return {
      things: [],
    }
  },
  async mounted() {
    const res = await axios.get(`${process.env.VUE_APP_API_BASE_URI}/directory/things/`)
    this.things = res.data
  }
}
</script>

<style scoped>
</style>

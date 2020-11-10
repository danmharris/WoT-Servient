<template>
  <div id="app">
    <div class="page-container">
      <md-app md-mode="reveal">
        <md-app-toolbar class="md-primary">
          <md-button class="md-icon-button" @click="menuVisible = true">
            <md-icon>menu</md-icon>
          </md-button>
          <span class="md-title">WoT Client</span>
        </md-app-toolbar>
        <md-app-drawer :md-active.sync="menuVisible" md-swipeable>
          <md-toolbar class="md-transparent" md-elevation="0">
            Menu
          </md-toolbar>
          <md-list>
            <md-list-item>
              <router-link to="/">Things</router-link>
            </md-list-item>
          </md-list>
        </md-app-drawer>
        <md-app-content>
          <router-view></router-view>
        </md-app-content>
      </md-app>
    </div>
  </div>
</template>

<script>

export default {
  name: 'App',
  data: function () {
    return {
      menuVisible: false,
    }
  },
}
</script>

<style>
.md-app {
  height: 100vh;
}
</style>

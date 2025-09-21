<template>
  <div id="app">
    <NavigationBar />
    <router-view />
  </div>
</template>

<script>
import NavigationBar from './components/NavigationBar.vue'

export default {
  name: 'App',
  components: {
    NavigationBar
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #ffffff;
  min-height: 100vh;
  background: #000000;
  line-height: 1.5;
}

body {
  margin: 0;
  padding: 0;
  background: #000000;
  overflow-x: hidden;
}

/* Global scroll behavior */
html {
  scroll-behavior: smooth;
}

/* Custom scrollbar for dark theme */
::-webkit-scrollbar {
  width: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
  border-radius: 5px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
}

/* Selection styling */
::selection {
  background: rgba(0, 150, 255, 0.4); /* nice blue highlight */
}

::-moz-selection {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

/* Focus styles for accessibility */
*:focus {
  outline: 2px solid rgba(255, 255, 255, 0.3);
  outline-offset: 2px;
}

/* Smooth transitions for all interactive elements */
* {
  transition: all 0.2s ease-in-out;
}

/* Font loading optimization */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global text contrast improvements */
h1, h2, h3, h4, h5, h6 {
  color: #ffffff;
  font-weight: 600;
}

p {
  color: #e0e0e0;
}

/* Enhanced focus for better accessibility */
button:focus,
input:focus,
textarea:focus,
select:focus {
  outline: 2px solid rgba(255, 255, 255, 0.5);
  outline-offset: 2px;
}

/* Improved readability */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>

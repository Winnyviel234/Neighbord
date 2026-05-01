export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        neighbor: {
          navy: '#062b5f',
          blue: '#1469b8',
          sky: '#38a7e8',
          green: '#2f9b2e',
          leaf: '#86c45f',
          mist: '#eef7fb'
        }
      },
      boxShadow: {
        soft: '0 18px 45px rgba(6, 43, 95, 0.10)'
      }
    }
  },
  plugins: []
};


/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#0a0a0c',
                card: 'rgba(18, 18, 23, 0.7)',
                primary: '#6366f1',
                secondary: '#a855f7',
                accent: '#f43f5e',
            },
        },
    },
    plugins: [],
}

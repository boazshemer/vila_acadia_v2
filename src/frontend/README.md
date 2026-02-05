# Vila Acadia Frontend

Modern, mobile-first React application for employee timesheet and tip management.

## Features

### Employee App
- 🔐 PIN-based authentication
- ⏰ Time entry with auto-calculation
- 📱 Mobile-optimized interface
- ✨ Smooth animations
- 🎯 15-second submission goal

### Manager App
- 🛡️ Password-protected access
- 💰 Daily tip input with calculations
- 👥 Employee list view
- 📊 Real-time formula preview

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **React Router** - Navigation
- **Axios** - API calls
- **React Hot Toast** - Notifications
- **Lucide React** - Icons

## Development Setup

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
# Navigate to frontend directory
cd src/frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at http://localhost:3000

### Development Server

The Vite dev server includes:
- ⚡ Hot Module Replacement (HMR)
- 🔄 API proxy to backend (no CORS issues)
- 📦 Automatic dependency optimization

## Project Structure

```
src/frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable components
│   │   └── LoadingSpinner.jsx
│   ├── pages/           # Page components
│   │   ├── EmployeeLogin.jsx
│   │   ├── EmployeeTimeEntry.jsx
│   │   ├── ManagerLogin.jsx
│   │   └── ManagerDashboard.jsx
│   ├── services/        # API service layer
│   │   └── api.js
│   ├── utils/           # Utility functions
│   │   └── timeCalculator.js
│   ├── App.jsx          # Main app with routing
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind configuration
└── postcss.config.js    # PostCSS configuration
```

## API Integration

### Proxy Configuration

Development requests to `/api/*` are proxied to `http://localhost:8000`:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

### API Methods

```javascript
import { authAPI, hoursAPI, managerAPI } from './services/api';

// Employee authentication
const result = await authAPI.verify('John Doe', '1234');

// Submit hours
const result = await hoursAPI.submit({
  employee_name: 'John Doe',
  date: '2026-01-28',
  start_time: '09:00',
  end_time: '17:00'
});

// Manager submit tips
const result = await managerAPI.submitTips({
  date: '2026-01-28',
  total_tips: 500.00
});
```

## Mobile Optimization

### Design Principles

- ✅ Mobile-first approach
- ✅ Touch-friendly buttons (min 44x44px)
- ✅ Large input fields
- ✅ Clear visual hierarchy
- ✅ Fast loading (<2s)
- ✅ Responsive grid layouts

### Breakpoints

```javascript
// Tailwind breakpoints
sm: '640px'   // Small devices
md: '768px'   // Medium devices
lg: '1024px'  // Large devices
xl: '1280px'  // Extra large devices
```

### Testing on Mobile

1. Use Chrome DevTools device emulation
2. Test on actual devices:
   - iPhone (Safari)
   - Android (Chrome)
3. Check different orientations
4. Test touch interactions

## Components

### LoadingSpinner

```jsx
<LoadingSpinner size="md" message="Loading..." />
```

Sizes: `sm`, `md`, `lg`

### Toast Notifications

```javascript
import toast from 'react-hot-toast';

toast.success('Hours submitted!');
toast.error('Failed to submit');
toast.loading('Processing...');
```

## Styling

### Tailwind CSS

Custom theme configuration:

```javascript
// Primary color palette
primary-50  to  primary-900

// Custom components
.btn, .btn-primary, .btn-secondary
.input
.card
```

### Custom Classes

```css
.btn - Base button styles
.btn-primary - Primary action button
.btn-secondary - Secondary action button
.input - Form input styles
.card - Card container styles
```

## Build & Deploy

### Development

```bash
npm run dev
```

### Production Build

```bash
npm run build
```

Output in `dist/` folder.

### Preview Production Build

```bash
npm run preview
```

### Deploy to Railway/Vercel/Netlify

1. Build the project
2. Set environment variables:
   - `VITE_API_URL=https://your-backend.railway.app`
3. Deploy `dist/` folder

## Testing Checklist

- [ ] Employee login with valid PIN
- [ ] Employee login with invalid PIN
- [ ] Time entry with various time ranges
- [ ] Time entry with overnight shift
- [ ] Auto-calculation display updates
- [ ] Submission success/error handling
- [ ] Manager login
- [ ] Manager tip submission
- [ ] Mobile responsiveness
- [ ] Toast notifications
- [ ] Loading states
- [ ] Navigation between pages
- [ ] Logout functionality

## Troubleshooting

### API Requests Failing

1. Check backend is running on port 8000
2. Check network tab in browser DevTools
3. Verify proxy configuration in `vite.config.js`

### Styles Not Loading

1. Clear browser cache
2. Restart dev server
3. Check Tailwind CSS configuration

### Build Errors

1. Clear `node_modules` and reinstall:
   ```bash
   rm -rf node_modules
   npm install
   ```
2. Check for TypeScript errors
3. Verify all imports are correct

## Performance

### Metrics

- Initial load: <2s
- Time to interactive: <3s
- Form submission: <1s

### Optimization

- Code splitting with React.lazy()
- Image optimization
- Minification in production
- Gzip compression

## Accessibility

- ✅ Semantic HTML
- ✅ ARIA labels
- ✅ Keyboard navigation
- ✅ Focus indicators
- ✅ High contrast text
- ✅ Touch targets ≥44px

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow existing code style
2. Use TypeScript for new files (optional)
3. Test on mobile devices
4. Update documentation

## License

Same as parent project

---

**For backend API documentation, see `/docs/PHASE2_COMPLETE.md`**



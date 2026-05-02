# LUMINARK Overwatch Demo

A professional, investor-ready demonstration of the LUMINARK AI output validation and compliance checking platform.

## Overview

LUMINARK Overwatch is a real-time validation engine that ensures AI-generated outputs meet compliance, quality, and safety standards. This demo showcases the core functionality with an intuitive, audit-ready interface designed for developers, partners, and investors.

**Brand:** LUMINARK  
**Legal Entity:** Meridian Axiom Alignment Technologies (Ma'at)

## Key Features

### 1. Real-Time Validation
- Submit AI-generated text for instant compliance analysis
- Receive structured validation results with compliance scores
- Support for custom validation rules and audit metadata

### 2. Audit-Ready Output
- JSON-formatted responses suitable for compliance records
- Detailed scoring and categorization (Pass/Caution/Fail)
- Copy-to-clipboard functionality for easy integration

### 3. Health Monitoring
- API health checks with connection status
- Timeout handling and error recovery
- Real-time feedback on system availability

### 4. Professional Interface
- Minimalist design emphasizing clarity and precision
- Responsive layout for desktop and mobile presentations
- Branded hero section with technical credibility

## Technology Stack

- **Frontend:** React 19 + TypeScript
- **Styling:** Tailwind CSS 4 + shadcn/ui components
- **Icons:** Lucide React
- **Build Tool:** Vite
- **Design:** Minimalist Precision (Swiss Modernism influenced)

## Project Structure

```
client/
  src/
    pages/
      Home.tsx          # Main demo interface
    components/
      ValidationBadge.tsx    # Validation result display
      JsonOutput.tsx         # JSON output with copy functionality
    hooks/
      useValidation.ts       # Validation logic and state management
      useHealthCheck.ts      # API health checking
    index.css          # Global styles and design tokens
    App.tsx            # Root component with routing
  public/              # Static assets
  index.html           # Entry point
package.json           # Dependencies and scripts
```

## Design Philosophy

The interface follows **Minimalist Precision** design principles:

- **Clarity through Simplification:** Information hierarchy via spatial relationships, not decoration
- **Technical Authority:** IBM Plex Mono for headings and code, Inter for body text
- **Color Strategy:** Deep charcoal backgrounds (#0F1117) with cyan accents (#00D9FF) for validation states
- **Audit Focus:** Emphasis on readable, structured output suitable for compliance records
- **Responsive Design:** Full mobile-to-desktop support for flexible presentations

## Getting Started

### Prerequisites
- Node.js 18+ and pnpm
- Backend API running on `http://localhost:8080` (configurable)

### Installation

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build
```

The dev server runs on `http://localhost:3000` by default.

## API Integration

### Configuration
1. Enter your API base URL in the "API Configuration" section
2. Click "Health Check" to verify connectivity
3. The demo will communicate with the following endpoints:

#### Health Check
```
GET /health
Response: { ok: boolean }
```

#### Validation
```
POST /validate
Content-Type: application/json

Request Body:
{
  "text": "AI output to validate",
  "source": "overwatch-demo",
  "meta": {
    "demo": true,
    "timestamp": "2026-02-15T19:00:00Z"
  }
}

Response:
{
  "badge": "pass" | "caution" | "fail",
  "overall_score": 0.95,
  ...additional fields
}
```

## Demo Flow

The interface guides users through a standard validation workflow:

1. **Load Example:** Click "Load Risky Example" or "Load Safe Example"
2. **Validate:** Click the "Validate" button to submit for analysis
3. **Review Results:** View compliance score and validation badge
4. **Inspect Output:** Review audit-ready JSON response

## Components

### ValidationBadge
Displays validation results with color-coded states:
- **Pass** (Green): Compliant output
- **Caution** (Amber): Review recommended
- **Fail** (Red): Non-compliant output

### JsonOutput
Renders JSON responses with:
- Syntax highlighting
- Copy-to-clipboard functionality
- Scrollable overflow handling
- Monospace formatting for readability

## Hooks

### useValidation(apiBase)
Manages validation state and API communication:
```typescript
const { result, loading, error, validate, reset } = useValidation(apiBase);
await validate(textToValidate);
```

### useHealthCheck(apiBase)
Monitors API health with timeout handling:
```typescript
const { ok, message, loading, check } = useHealthCheck(apiBase);
await check();
```

## Styling & Customization

### Color Palette
- **Primary Accent:** `#00D9FF` (Cyan)
- **Background:** `#0F1117` (Deep Charcoal)
- **Text:** `#1E293B` (Dark Slate)
- **Success:** `#10B981` (Emerald)
- **Warning:** `#F59E0B` (Amber)
- **Error:** `#EF4444` (Red)

### Typography
- **Headings:** IBM Plex Mono (600-700 weight)
- **Body:** Inter (400-600 weight)
- **Code:** IBM Plex Mono (400 weight)

All colors and fonts are defined in `client/src/index.css` using CSS variables for easy customization.

## Deployment

### Manus Hosting
The application is deployed on Manus with automatic HTTPS and custom domain support.

**Current URL:** [Available in Management UI]

### Static Build
```bash
pnpm build
# Output: dist/public/
```

The build is fully static and can be deployed to any CDN or static hosting service.

## Performance Optimizations

- Lazy component loading via React.lazy
- Optimized font loading with Google Fonts preconnect
- CSS variable-based theming for minimal runtime overhead
- Minimal animation overhead with CSS transitions
- Responsive image handling with proper sizing

## Accessibility

- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus ring indicators
- Color contrast compliance (WCAG AA+)
- Screen reader friendly

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Android)

## Error Handling

The application includes robust error handling:

- **API Timeouts:** 5-second timeout with user feedback
- **Network Errors:** Clear error messages with retry options
- **Validation Errors:** Input validation before API calls
- **JSON Parsing:** Safe handling of malformed responses

## Future Enhancements

- Batch validation for multiple inputs
- Custom validation rule configuration
- Historical audit log viewer
- Export validation reports (PDF/CSV)
- Real-time API monitoring dashboard
- Dark mode toggle
- Multi-language support

## Support & Feedback

For questions, issues, or feature requests, please contact the development team or submit feedback through the Manus platform.

## License

Proprietary - LUMINARK by Meridian Axiom Alignment Technologies (Ma'at)

---

**Version:** 1.0.0  
**Last Updated:** February 15, 2026  
**Status:** Production Ready

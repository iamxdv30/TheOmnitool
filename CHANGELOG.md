# Changelog

All notable changes to this project will be documented in this file.

## [1.4.1] - 2025-08-31
### Highlights

### Batch 1 release

### ✨ Added
- **Admin Dashboard**: Complete user management interface with search and pagination
- **Character Counter Tool**: Adjustable character limits with real-time validation and visual feedback
- **Advanced Search System**: Reusable search with pagination (8 items per page) and item counting
- **Client-side Form Validation**: Real-time validation with contextual error messages above input fields
- **Company Logo**: Responsive logo with automatic theme adaptation and brightness filters
- **Version Display**: Automatic version number parsing and display in footer
- **Flash Message System**: Centralized, theme-aware flash messages with proper mobile alignment

### 🎨 Enhanced
- **Dark Theme System**: Comprehensive CSS variable system with standardized `html.dark` selector
- **Mobile Responsiveness**: Optimized layouts for 320px+ devices with improved touch targets
- **Form Styling**: Consistent 2px borders, enhanced focus states with orange accent and glow effects
- **Button Interactions**: Improved hover animations and visual feedback across all components
- **Typography**: Better contrast and readability in both light and dark modes

### 🔧 Technical Improvements
- **JavaScript Modernization**: Complete migration from inline scripts to modular ES6 architecture
- **Code Organization**: Implemented `utils/`, `modules/`, `pages/` directory structure
- **Performance**: Applied IIFE patterns, event delegation, and efficient search algorithms (O(n) complexity)
- **Error Handling**: Enhanced SMTP authentication and user-friendly error messages
- **Accessibility**: Added proper ARIA attributes and keyboard navigation support

### 🐛 Fixed
- Canada tax calculator province selection and add item functionality
- Email verification ReferenceError in contact.js fetch response handling
- Country redirection between US/Canada tax calculators
- Email templates CRUD operations and API endpoint routing
- Mobile UI text wrapping and search bar alignment issues
- Dark theme toggle functionality and JavaScript implementation

### 💔 Breaking Changes
- All templates now use external JavaScript modules instead of inline scripts
- Dark theme selector changed from `body.dark-theme` to `html.dark`
- Requires proper static file serving for new modular JS architecture

### 📱 Mobile Optimizations
- Enhanced responsive behavior across all screen sizes
- Improved touch targets and mobile form interactions
- Optimized container layouts for small screens (320px minimum)
- Better viewport handling and touch-friendly controls

### Batch 2 release
### Highlights

- Captcha in Login
- Simple registration

---


## [1.4.0] - 2025-06-20
### Highlights

## [Unreleased] - Captcha in Login, Simple registration, and API request limit

✨ Added  - 2025-06-20

🔐 Forgot Password functionality with a secure, multi-step reset process:
- Users can initiate a password reset from the new /forgot_password page.
- System generates a time-limited (1 hour) secure token using itsdangerous.
- An email with a reset link is sent via Flask-Mail.
- Users can reset their password through the /reset_password/<token> page.
- On success, the user’s password is updated and they can log in again.

🧭 UI update:
- Added “Forgot Password?” link to the login page for quick access

---

## [1.3.0] - 2025-06-08
### Highlights

⚙️ Architectural Refactor
- Split models into `base.py`, `users.py`, `tools.py`, `auth.py`
- Implemented Factory Pattern for User creation
- Implemented Strategy Pattern for password hashing
- Cleaned up `__init__.py` compatibility layer
- Fixed circular import issues with local imports
- All routes updated to new model import paths

🧑‍💻 Code Quality
- More modular, maintainable, and extensible codebase
- Ready for future scaling and testing improvements

🌐 UI
- Modern sliding theme toggle
- Modernized Index page, About page, User Dashboard
- Improved Accessibility and Responsive Design

🧮 Tax Calculators
- Advanced Sales-before-tax logic
- Complex discount scenarios
- Consistent Canada Tax Calculator logic
- Client-side state preservation

🚀 DevOps
- Stable CI/CD pipeline
- Heroku Deployment tested
- Database Backup/Restore in production pipeline

---

## [1.2.0] - 2025-06-02
- Modern sliding theme toggle for Dark/Light mode
- Modernized Index page and About page
- Accessibility improvements
- UI fixes and consistency

## [1.1.0] - 2025-03-24
- Sales-before-tax logic support
- Complex discount scenario support
- Canada Tax Calculator updated to match global logic
- Full client-side state preservation for Tax Calculators
- Client-side calculation prevents form refreshes
- Advanced tax calculation tests

## [1.0.0] - 2024-10-27
- Email Verification
- Improved Contact Form
- Testing Coverage
- Database Backup/Restore
- CI/CD Workflow ready for Heroku deploy

## [0.9.0] - 2024-10-11
- Initial CI/CD pipeline setup
- Heroku deployment working
- Initial test cases added

## [0.5.0] - 2024-09-27
- Canada Tax Calculator
- Profile Page
- Admin and SuperAdmin dashboards
- Tool access system

## [0.1.0] - 2024-09-17
- Initial Tax Calculator
- User Registration and Login
- Basic UI and Dark Theme toggle

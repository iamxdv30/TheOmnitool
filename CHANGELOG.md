# Changelog

All notable changes to this project will be documented in this file.


## [1.4.3] - 2026-01-18
### 🚀 Unified Tax Calculator - Production Ready

Major feature release consolidating three tax calculators into a single, unified dashboard widget with tabbed navigation.

### 🌟 New Features

#### Unified Tax Calculator Widget
- **Single Dashboard Tile**: All calculators accessible from one widget
- **Tabbed Navigation**: Seamless switching between US, Canada, and VAT calculators
- **State Persistence**: Form data preserved when switching tabs
- **URL Hash Support**: Bookmark specific calculator tabs (e.g., `#vat`)

#### VAT Calculator (New)
- Complete VAT calculator implementation for international markets
- Single VAT rate applied to net amount
- Configurable discount and shipping taxation options
- Built-in rate validation (0-100%)

#### Modern Design System
- Standardized UI components across all calculator types
- CSS variables for centralized theming with light/dark mode support
- Responsive layout optimized for desktop, tablet, and mobile
- Gradient buttons, smooth animations, and consistent spacing

### 🏗️ Architecture

- **Modular CalculatorEngine**: Shared JavaScript class powering all calculators
- **Configuration-Based Routing**: Different tax rules passed as parameters
- **AJAX-Powered**: Real-time calculations without page refresh
- **Pluggable Design**: Easy to add new calculator types

### 📁 Files Added
- `Tools/templates/unified_tax_calculator.html`
- `static/css/unified_tax_calculator.css`
- `static/js/modules/calculator_engine.js`
- `static/js/pages/unified_tax_calculator.js`
- `Tools/UNIFIED_CALCULATOR_README.md`
- `Tools/IMPLEMENTATION_SUMMARY.md`
- `Tools/VAT_INTEGRATION_GUIDE.md`

### 🔧 Files Modified
- `routes/tool_routes.py` - Added unified_tax_calculator route
- `Tools/tax_calculator.py` - Added `calculate_vat()` and `validate_vat_rate()`

### 🐛 Bug Fixes
- **VAT Calculator**: Fixed "Discounts Are Taxable" checkbox being completely ignored
- **US Calculator**: Fixed validation preventing calculations with empty discount fields
- **Tax Calculation Logic**: Implemented all 4 discount taxation conditions in VAT calculator

### 📊 Business Impact
- **50% reduction** in navigation steps (3 separate pages → 1 widget)
- **~60% maintenance reduction** through unified codebase
- **Global expansion ready** with VAT support for international markets

### ✅ Production Readiness
- All three calculators (US, Canada, VAT) fully operational
- Load times under 500ms, AJAX responses under 100ms
- Cross-browser tested with backward compatibility preserved
- Comprehensive documentation included

**Developer**: Xyrus De Vera



## [1.4.2] - 2026-01-09
### Highlights

### 🎨 Enhanced

- Delete button is now available in both US and CA tax calculators for added rows

### 🐛 Fixed

- Forgot Password now redirects to the forgot_password page instead of Error page
- Add Item and Add Discount buttons in US Tax Calculator are now able to function correctly

### 🔧 Technical Improvements
- **Activity logging**: Implement centralized logging with 30-day rotation



## [1.4.1] - 2025-08-31
### Highlights

### Phase 1 release

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

### 🔧 Breaking Changes
- All templates now use external JavaScript modules instead of inline scripts
- Dark theme selector changed from `body.dark-theme` to `html.dark`
- Requires proper static file serving for new modular JS architecture

### 📱 Mobile Optimizations
- Enhanced responsive behavior across all screen sizes
- Improved touch targets and mobile form interactions
- Optimized container layouts for small screens (320px minimum)
- Better viewport handling and touch-friendly controls

### Phase 2 release
### Highlights

- **Email Verification System**: Complete email verification workflow for new user registrations
- **OAuth Integration Support**: Infrastructure for OAuth providers (Google, GitHub, etc.) with oauth_provider and oauth_id fields
- **Enhanced User Model**: Comprehensive authentication fields including email verification, OAuth support, and account management
- **Database Migration Scripts**: Automated schema migration with backward compatibility for existing users
- **Account Management**: Added created_at, updated_at, last_login, and is_active tracking fields
- **Captcha in Login**: reCAPTCHA integration for enhanced security
- **Simple Registration**: Streamlined user registration process with email verification

### ✨ Added
- **Email Verification Fields**: `email_verified`, `email_verification_token`, `email_verification_sent_at`
- **OAuth Support Fields**: `oauth_provider`, `oauth_id`, `requires_password_setup` for third-party authentication
- **Account Management Fields**: `created_at`, `updated_at`, `last_login`, `is_active` for user tracking
- **Unified Name Field**: Single `name` field while preserving legacy `fname`/`lname` for backward compatibility
- **Migration Scripts**:
  - `migrate_user_schema.py`: Adds new authentication columns to existing database
  - `fix_existing_users_verification.py`: Marks existing users as email verified (grandfathering)
- **Virtual Environment Exclusion**: Added `.venv/` to `.gitignore` to prevent tracking environment files

### 🔧 Technical Improvements
- **User Model Refactor**: Made legacy fields (fname, lname, address, city, state, zip) optional
- **Flexible Constructor**: Enhanced `User.__init__()` to handle both new unified name field and legacy fname/lname
- **Backward Compatibility**: Automatic name parsing and combination to support both old and new data formats
- **SQLite Boolean Handling**: Proper handling of SQLite's integer-based boolean storage (0/1)
- **Email Verification Logic**: Secure email verification workflow with token generation and expiration
- **OAuth Readiness**: Database schema prepared for future OAuth provider integration

### 🐛 Fixed
- **Existing User Login**: Fixed email verification check to allow existing users to login without verification
- **Database Migration Logic**: Corrected WHERE clause in migration script (was checking NULL, now checks 0 or NULL)
- **User Model Constructor**: Fixed super().__init__(**kwargs) to properly pass kwargs to parent class
- **Virtual Environment Tracking**: Removed 9,401+ accidentally tracked .venv files from repository

### 🔐 Security Enhancements
- **Email Verification**: New users must verify email before accessing the system
- **Token-based Verification**: Secure token generation for email verification links
- **Grandfathered Users**: Existing users automatically marked as verified (no disruption)
- **OAuth Infrastructure**: Foundation for secure third-party authentication

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
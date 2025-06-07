# Changelog

All notable changes to this project will be documented in this file.

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

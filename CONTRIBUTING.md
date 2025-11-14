# Contributing to AAROHAN

Thank you for your interest in contributing to AAROHAN! This document provides guidelines and instructions for contributing.

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How Can I Contribute?](#-how-can-i-contribute)
- [Development Setup](#-development-setup)
- [Coding Standards](#-coding-standards)
- [Pull Request Process](#-pull-request-process)
- [Issue Guidelines](#-issue-guidelines)
- [Community](#-community)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and professional in all interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct which could be considered inappropriate

---

## 🎯 How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
- Check the [existing issues](https://github.com/Gaurav8302/AROHANN/issues)
- Try the latest version from `main` branch
- Collect information about the bug

**What to include in bug reports:**
- Clear and descriptive title
- Exact steps to reproduce
- Expected vs. actual behavior
- Screenshots (if applicable)
- Environment details:
  - OS and version
  - Python version
  - Node.js version
  - Browser (for frontend issues)

**Example bug report:**
```markdown
**Title:** Dashboard fails to load student data

**Description:**
When opening the dashboard, student data doesn't load and console shows Firebase error.

**Steps to Reproduce:**
1. Navigate to dashboard
2. Wait for data to load
3. Check browser console

**Expected Behavior:**
Dashboard should display 56 students

**Actual Behavior:**
Blank screen with error: "Firebase: permission denied"

**Environment:**
- OS: Windows 11
- Browser: Chrome 120
- Backend: Running on localhost:8000
```

### Suggesting Enhancements

**Before suggesting:**
- Check if it's already in the roadmap
- Search existing enhancement requests

**Enhancement template:**
```markdown
**Feature Description:**
Brief description of the feature

**Use Case:**
Who would benefit and how?

**Proposed Solution:**
How should this work?

**Alternatives Considered:**
Other approaches you've thought about
```

### Contributing Code

We welcome code contributions! See [Development Setup](#-development-setup) below.

**Good first issues:**
- Look for issues labeled `good first issue`
- Documentation improvements
- Bug fixes
- Test coverage improvements

---

## 💻 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/AROHANN.git
cd AROHANN

# Add upstream remote
git remote add upstream https://github.com/Gaurav8302/AROHANN.git
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

Examples:
- `feature/add-email-notifications`
- `fix/dashboard-loading-error`
- `docs/update-setup-guide`

### 3. Set Up Development Environment

Follow the [SETUP.md](./SETUP.md) guide to:
- Install dependencies
- Configure environment variables
- Run the application locally

### 4. Make Changes

Follow the [Coding Standards](#-coding-standards) below.

### 5. Test Your Changes

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Manual testing
# - Test all affected features
# - Check console for errors
# - Verify responsive design
```

### 6. Commit Your Changes

```bash
git add .
git commit -m "feat: add email notification feature"
```

**Commit message format:**
```
<type>: <subject>

<body> (optional)

<footer> (optional)
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Formatting, missing semicolons, etc.
- `refactor` - Code restructuring
- `test` - Adding tests
- `chore` - Maintenance tasks

**Examples:**
```
feat: add email notification system

Implemented automated email notifications for:
- Orange phase escalations
- Red phase alerts
- Parent notifications

Closes #123
```

```
fix: resolve dashboard loading timeout

Fixed Firebase query timeout by adding retry logic
and increasing timeout from 5s to 10s

Fixes #456
```

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## 📝 Coding Standards

### Python (Backend)

**Style Guide:** Follow [PEP 8](https://pep8.org/)

**Tools:**
```bash
# Format with black
black app/

# Check with flake8
flake8 app/

# Type checking with mypy (optional)
mypy app/
```

**Best Practices:**
- Use type hints for function parameters and returns
- Write docstrings for all public functions/classes
- Keep functions small and focused
- Use meaningful variable names
- Handle errors gracefully

**Example:**
```python
from typing import Dict, List

def predict_dropout_risk(
    student_data: Dict[str, float],
    threshold: float = 0.5
) -> Dict[str, any]:
    """
    Predict dropout risk for a student.
    
    Args:
        student_data: Dictionary containing student features
        threshold: Classification threshold (default: 0.5)
        
    Returns:
        Dictionary with prediction results
        
    Raises:
        ValueError: If required fields are missing
    """
    # Implementation
    pass
```

### TypeScript/React (Frontend)

**Style Guide:** Follow [Airbnb Style Guide](https://github.com/airbnb/javascript)

**Tools:**
```bash
# Lint with ESLint
npm run lint

# Format with Prettier (if configured)
npm run format
```

**Best Practices:**
- Use functional components and hooks
- Prefer TypeScript over JavaScript
- Use meaningful component names
- Extract reusable logic into custom hooks
- Keep components small and focused
- Use proper prop types

**Example:**
```typescript
interface StudentCardProps {
  student: Student;
  onView: (id: string) => void;
}

export const StudentCard: React.FC<StudentCardProps> = ({ student, onView }) => {
  const riskColor = getRiskColor(student.phase);
  
  return (
    <Card className="student-card">
      <RiskBadge phase={student.phase} />
      <h3>{student.name}</h3>
      <Button onClick={() => onView(student.id)}>
        View Details
      </Button>
    </Card>
  );
};
```

### General Best Practices

**Code Organization:**
- Group related code together
- Use clear folder structure
- Avoid circular dependencies
- Keep files focused and manageable

**Naming Conventions:**
- **Python**: `snake_case` for variables/functions, `PascalCase` for classes
- **TypeScript**: `camelCase` for variables/functions, `PascalCase` for components/types
- **Files**: Match the primary export (e.g., `StudentCard.tsx` for `StudentCard` component)

**Comments:**
- Write self-documenting code first
- Add comments for complex logic
- Update comments when code changes
- Avoid obvious comments

**Error Handling:**
- Catch specific exceptions
- Provide meaningful error messages
- Log errors appropriately
- Never silence errors silently

---

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts with main
- [ ] Tested locally

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks:** CI/CD runs tests and linting
2. **Code Review:** Team member reviews code
3. **Feedback:** Address review comments
4. **Approval:** At least one approval required
5. **Merge:** Squash and merge into main

### After Merge

- Delete your feature branch
- Update your local main branch
- Close any related issues

---

## 🐛 Issue Guidelines

### Creating Issues

**Use appropriate labels:**
- `bug` - Something isn't working
- `enhancement` - New feature request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Need community help
- `question` - Questions about the project

**Template:**
```markdown
**Type:** [Bug / Feature / Documentation]

**Description:**
Clear description of issue/request

**Additional Context:**
Any other relevant information
```

### Working on Issues

1. **Comment on the issue** to claim it
2. **Wait for confirmation** from maintainers
3. **Create a branch** and start working
4. **Link PR to issue** when ready

---

## 👥 Community

### Communication Channels

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** Questions and discussions
- **Pull Requests:** Code contributions

### Recognition

Contributors will be:
- Listed in `CONTRIBUTORS.md`
- Credited in release notes
- Mentioned in project documentation

### Becoming a Maintainer

Regular contributors may be invited to become maintainers. Criteria:
- Consistent high-quality contributions
- Good understanding of the codebase
- Active participation in reviews
- Alignment with project goals

---

## 📚 Additional Resources

- [Setup Guide](./SETUP.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Testing Guide](./TESTING_GUIDE.md)
- [Project README](./README.md)

---

## ❓ Questions?

- Check [existing issues](https://github.com/Gaurav8302/AROHANN/issues)
- Open a new issue with label `question`
- Contact maintainers

---

<div align="center">

**Thank you for contributing to AAROHAN! 🎉**

Together, we can help prevent student dropouts through technology.

</div>

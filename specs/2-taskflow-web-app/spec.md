# Feature Specification: TaskFlow Web - Multi-User Todo Application

**Feature Branch**: `2-taskflow-web-app`
**Created**: 2025-12-31
**Status**: Draft
**Input**: Phase 2: Full-Stack Web Application - Transform Phase 1 console app into a beautiful, secure, multi-user web application with persistent storage, authentication, and a REST API

## Project Overview

**Name**: TaskFlow Web
**Purpose**: Multi-user web-based todo application with authentication and persistent storage
**Evolution**: Transforms Phase 1 console app into modern web application
**Scope**: 5 Basic Level CRUD features + User authentication

**Success Vision**:
- All Phase 1 features work via web interface
- Users can create accounts and sign in
- Each user has private task list
- Data persists in PostgreSQL database
- Frontend deployed and accessible via URL
- Application is secure and reliable

## User Scenarios & Testing

### User Story 1 - User Registration (Priority: P1)

**User Journey**: New users can create an account to access the application

A new user visits the application URL and sees a clean landing page with options to sign in or sign up. They click "Sign Up" and are taken to a registration form where they enter their email and password. After submitting valid credentials, their account is created, they are automatically signed in, and redirected to an empty dashboard ready to create their first task.

**Why this priority**: Without user registration, there is no multi-user capability. This is the entry point for all users and must work first.

**Independent Test**: Can be fully tested by navigating to /signup, filling the form with valid credentials, submitting, and verifying the user is created in the database and automatically signed in to /dashboard.

**Acceptance Scenarios**:

1. **Given** a new user visits the landing page, **When** they click "Sign Up" and enter valid email "john@example.com" and password "SecurePass123", **Then** their account is created, they are automatically signed in, and redirected to /dashboard with a welcome message
2. **Given** a user on the signup page, **When** they enter an email that already exists, **Then** they see error message "This email is already registered. Try signing in."
3. **Given** a user on the signup page, **When** they enter a password with less than 8 characters, **Then** they see error message "Password must be at least 8 characters"
4. **Given** a user on the signup page, **When** they enter mismatched passwords in confirm field, **Then** they see error message "Passwords must match"
5. **Given** a user submits the signup form, **When** the request is processing, **Then** the submit button shows a loading spinner and is disabled to prevent duplicate submissions
6. **Given** a user successfully signs up, **When** they check their browser cookies, **Then** a JWT token is stored in an httpOnly cookie valid for 7 days

---

### User Story 2 - User Sign In (Priority: P1)

**User Journey**: Returning users can access their account and existing tasks

A returning user visits the application and sees the sign-in page. They enter their email and password, click "Sign In", and are authenticated. Upon successful authentication, they are redirected to their dashboard where they see all their previously created tasks. If they close the browser and return within 7 days, they remain signed in.

**Why this priority**: Equal priority with registration as users need both to create accounts and return to them. Without sign-in, returning users cannot access their data.

**Independent Test**: Can be fully tested by creating a user account, signing out, then signing back in with correct credentials and verifying access to dashboard and tasks.

**Acceptance Scenarios**:

1. **Given** an existing user with email "john@example.com" and password "SecurePass123", **When** they enter correct credentials and click "Sign In", **Then** they are authenticated and redirected to /dashboard showing their tasks
2. **Given** a user on the signin page, **When** they enter incorrect password, **Then** they see generic error "Invalid email or password" (for security)
3. **Given** a user on the signin page, **When** they enter non-existent email, **Then** they see generic error "Invalid email or password" (for security)
4. **Given** a user successfully signs in, **When** they close browser and return within 7 days, **Then** they are still authenticated and can access /dashboard directly
5. **Given** a user's JWT token expires (after 7 days), **When** they try to access /dashboard, **Then** they are redirected to signin page with message "Session expired. Please sign in."
6. **Given** an unauthenticated user, **When** they try to access /dashboard directly, **Then** they are redirected to signin page

---

### User Story 3 - Add Task (Priority: P2)

**User Journey**: Authenticated users can create new tasks with title and optional description

A signed-in user on their dashboard sees an "Add New Task" form at the top of the page. They type a task title like "Buy groceries" and optionally add a description like "Milk, eggs, bread, fruits". When they click "Add Task" or press Enter, the task is validated, saved to the database with their user_id, and immediately appears in their task list below. The form clears, ready for the next task.

**Why this priority**: This is the primary value-add feature - creating tasks. While authentication (P1) enables multi-user capability, this feature delivers the core functionality users came for.

**Independent Test**: Can be fully tested by signing in as a user, entering a task title in the form, submitting, and verifying the task appears in the list and is persisted in the database with the correct user_id.

**Acceptance Scenarios**:

1. **Given** an authenticated user on /dashboard, **When** they enter title "Buy groceries" and click "Add Task", **Then** the task is created, saved to database, displayed in their task list, form is cleared, and success toast "✓ Task created!" appears
2. **Given** an authenticated user on /dashboard, **When** they enter title "Buy groceries" and description "Milk, eggs, bread", **Then** both title and description are saved and displayed in the task card
3. **Given** a user tries to submit empty title, **When** they click "Add Task", **Then** they see inline error "Title cannot be empty"
4. **Given** a user enters a title with 205 characters, **When** the character count reaches 200, **Then** they see error "Title must be 200 characters or less (currently: 205)"
5. **Given** a user enters a description with 1050 characters, **When** the character count reaches 1000, **Then** they see error "Description too long"
6. **Given** a user submits the form, **When** the request is processing, **Then** the button shows loading spinner and is disabled
7. **Given** a network error occurs during task creation, **When** the request fails, **Then** user sees toast "Unable to save task. Please try again." and form data is preserved

---

### User Story 4 - View Tasks (Priority: P2)

**User Journey**: Authenticated users can see all their tasks displayed in a list

When a user signs in or refreshes their dashboard, the application loads all their tasks from the database and displays them in cards. Each task card shows the title, description (if present), completion status (checkbox), creation date, and action buttons (Edit, Delete). Completed tasks are visually distinct with strikethrough text. If the user has no tasks, a friendly empty state message encourages them to create their first task.

**Why this priority**: Same priority as "Add Task" because users need to see their tasks immediately after creating them. These two features work together to deliver the core experience.

**Independent Test**: Can be fully tested by signing in as a user with existing tasks and verifying all tasks are displayed correctly, or signing in as a new user and verifying the empty state appears.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 3 tasks in database, **When** they load /dashboard, **Then** all 3 tasks are displayed in cards sorted by creation date (newest first)
2. **Given** a task with completed=true, **When** displayed in the list, **Then** it shows a checked checkbox and title has strikethrough styling
3. **Given** a task with completed=false, **When** displayed in the list, **Then** it shows an unchecked checkbox and title has normal styling
4. **Given** an authenticated user with 0 tasks, **When** they load /dashboard, **Then** they see empty state with icon, message "No tasks yet", and encouragement "Create your first task above to get started!"
5. **Given** /dashboard is loading, **When** fetching tasks from API, **Then** a loading skeleton or spinner is displayed
6. **Given** User A with 5 tasks and User B with 3 tasks, **When** each user loads their dashboard, **Then** User A sees only their 5 tasks and User B sees only their 3 tasks (user isolation verified)
7. **Given** tasks are displayed, **When** counting tasks, **Then** the header shows "Your Tasks (3)" with accurate count

---

### User Story 5 - Edit Task (Priority: P3)

**User Journey**: Authenticated users can modify existing task title and description

A user viewing their task list clicks the "Edit" button on a task card. An edit interface appears (modal, inline, or separate page) with form inputs pre-filled with the current task values. The user modifies the title and/or description, then clicks "Save". The changes are validated, persisted to the database, and the task card updates to show the new values. A success message confirms the update.

**Why this priority**: Lower priority than create/view because users can still use the application productively without editing (just create new tasks). However, it's essential for correcting mistakes and updating task details.

**Independent Test**: Can be fully tested by creating a task, clicking its Edit button, changing the title and/or description, saving, and verifying the changes are persisted and displayed.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing a task, **When** they click "Edit" button, **Then** an edit form opens with title and description fields pre-filled with current values
2. **Given** a user in edit mode, **When** they change title to "Buy groceries and fruits" and click "Save", **Then** the task is updated in database, displayed with new title, edit mode closes, and success toast "✓ Task updated!" appears
3. **Given** a user in edit mode, **When** they change only the description, **Then** only the description is updated while title remains unchanged
4. **Given** a user in edit mode, **When** they try to save an empty title, **Then** they see inline error "Title cannot be empty"
5. **Given** a user in edit mode, **When** they click "Cancel", **Then** the edit form closes, no changes are saved, and task displays original values
6. **Given** User A tries to edit User B's task by manipulating the API request, **When** the backend receives the request, **Then** it returns 403 Forbidden with message "You don't have permission to edit this task"
7. **Given** a user tries to edit a task that was deleted by another process, **When** they submit the edit, **Then** they see error "This task no longer exists" and the task is removed from their list

---

### User Story 6 - Delete Task (Priority: P3)

**User Journey**: Authenticated users can permanently remove tasks from their list

A user viewing their task list clicks the "Delete" button on a task card. A confirmation dialog appears showing the task title and warning "This action cannot be undone." The user can click "Cancel" to abort, or "Delete" to confirm. If confirmed, the task is removed from the database and the task list, and a success message appears.

**Why this priority**: Same as Edit - useful but not critical for initial productivity. Users can work around lack of delete by ignoring completed tasks. However, it's important for maintaining a clean, relevant task list.

**Independent Test**: Can be fully tested by creating a task, clicking Delete, confirming in the dialog, and verifying the task is removed from both UI and database.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing a task, **When** they click "Delete" button, **Then** a confirmation dialog appears with title "Delete Task?", shows the task title "Buy groceries", and warning "This action cannot be undone."
2. **Given** a confirmation dialog is open, **When** the user clicks "Cancel", **Then** the dialog closes, task remains in list, and no API call is made
3. **Given** a confirmation dialog is open, **When** the user clicks "Delete" and confirms, **Then** the task is deleted from database, removed from UI with animation, dialog closes, and success toast "✓ Task deleted" appears
4. **Given** a user deletes a task, **When** they refresh the page, **Then** the deleted task does not reappear (deletion persisted)
5. **Given** User A tries to delete User B's task by manipulating the API request, **When** the backend receives the request, **Then** it returns 403 Forbidden with message "You don't have permission to delete this task"
6. **Given** multiple users viewing dashboards, **When** User A deletes their task, **Then** User B's dashboard is unaffected and shows all their tasks

---

### User Story 7 - Toggle Task Status (Priority: P3)

**User Journey**: Authenticated users can mark tasks as complete or pending by clicking a checkbox

A user viewing their task list sees a checkbox next to each task. When they click the checkbox on a pending task, it immediately shows as checked, the title gets strikethrough styling, and the change is saved to the database. Clicking again toggles it back to pending, removing the strikethrough. This provides quick visual feedback on task progress.

**Why this priority**: This completes the basic task lifecycle (create → complete → optionally edit/delete). While valuable, users can still track tasks mentally without this feature, making it lower priority than create/view.

**Independent Test**: Can be fully tested by creating a task, clicking its checkbox to toggle status, and verifying the UI updates immediately and the change persists after page refresh.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing a pending task (completed=false), **When** they click the checkbox, **Then** checkbox shows checked state, title gets strikethrough styling, and API call updates completed=true in database
2. **Given** an authenticated user viewing a completed task (completed=true), **When** they click the checkbox, **Then** checkbox shows unchecked state, strikethrough is removed, and API call updates completed=false in database
3. **Given** a user clicks a checkbox, **When** the UI updates optimistically, **Then** the change is visible instantly (before API response) providing immediate feedback
4. **Given** a network error occurs during toggle, **When** the API request fails, **Then** the checkbox reverts to previous state and error toast appears
5. **Given** a user toggles a task status, **When** they refresh the page, **Then** the task displays the updated status (persistence verified)
6. **Given** a task is marked complete, **When** displayed in list, **Then** the entire task card has visual distinction (dimmed text, strikethrough title, checked checkbox)
7. **Given** User A tries to toggle User B's task status, **When** the backend receives the request, **Then** it returns 403 Forbidden

---

### User Story 8 - User Sign Out (Priority: P3)

**User Journey**: Authenticated users can end their session and sign out

A signed-in user sees a "Sign Out" button in the dashboard header. When clicked, the JWT token is cleared from cookies, they are redirected to the signin page with a success message, and can no longer access protected routes without signing back in.

**Why this priority**: Lowest priority as users can simply close the browser or wait for token expiration. However, important for shared computers and explicit session management.

**Independent Test**: Can be fully tested by signing in, clicking "Sign Out", and verifying token is cleared and dashboard is no longer accessible.

**Acceptance Scenarios**:

1. **Given** an authenticated user on /dashboard, **When** they click "Sign Out" button in header, **Then** their JWT token is cleared, they are redirected to signin page, and see success message "You've been signed out successfully"
2. **Given** a user has signed out, **When** they try to access /dashboard, **Then** they are redirected to signin page
3. **Given** a user has signed out, **When** they check their cookies, **Then** the JWT token is no longer present

---

### Edge Cases

**Authentication Edge Cases**:
- What happens when a user tries to sign up with an invalid email format (no @, no domain)? → Show inline error "Please enter a valid email address"
- What happens when the signup request times out due to network issues? → Show error "Request timed out. Please try again." and preserve form data
- What happens when a user's token expires while they're actively using the app? → Redirect to signin with message "Session expired. Please sign in again."
- What happens when a user tries to access /dashboard without any authentication token? → Immediate redirect to signin page

**Task Creation Edge Cases**:
- What happens when a user enters a title with exactly 200 characters? → Accepted (boundary valid)
- What happens when a user enters a title with 201 characters? → Show error "Title must be 200 characters or less (currently: 201)"
- What happens when a user submits a task but database connection fails? → Show error "Something went wrong. Please try again." and preserve form data
- What happens when a user creates a task while offline? → Show error "Unable to connect. Check your internet connection."

**Task Viewing Edge Cases**:
- What happens when a user has 50+ tasks? → All displayed in Phase 2 (pagination deferred to future phase)
- What happens when a task title is extremely long (200 chars)? → Display with text wrapping or truncation with ellipsis
- What happens when database query fails while loading tasks? → Show error message "Unable to load tasks. Please refresh."
- What happens when two browser tabs are open with same user? → Each tab independently fetches tasks; changes in one tab not reflected in other until refresh (real-time sync out of scope)

**Task Editing Edge Cases**:
- What happens when User A edits a task that User B has deleted in another session? → Return 404 "This task no longer exists"
- What happens when a user tries to edit a task_id that doesn't exist? → Return 404 "Task not found"
- What happens when a user tries to edit by directly calling API with another user's user_id? → Return 403 Forbidden (user_id from token doesn't match path)

**Task Deletion Edge Cases**:
- What happens when a user clicks delete but closes the confirmation dialog by clicking outside? → Dialog closes, no deletion occurs
- What happens when a user tries to delete an already-deleted task (double-click scenario)? → Show message "Task already deleted" and remove from UI
- What happens when the only task is deleted? → Empty state appears

**Status Toggle Edge Cases**:
- What happens when a user rapidly clicks the checkbox multiple times? → Each click sends a toggle request; final state depends on last successful response
- What happens when the toggle request fails midway? → Revert optimistic UI update and show error
- What happens when a completed task is toggled back to pending after 30 days? → Works the same way; no time restrictions on toggling

**User Isolation Edge Cases**:
- What happens when User A tries to access /api/user-B-id/tasks with a manipulated request? → Backend verifies token user_id doesn't match path user_id, returns 403 Forbidden
- What happens when a user manually changes the user_id in the browser URL? → Frontend API client uses authenticated user's ID from auth context, ignoring URL; backend validates token
- What happens when two users have tasks with the same task_id (auto-increment collision)? → Cannot happen; task_id is globally unique in database; each user's tasks are filtered by user_id, not task_id

**CORS & Security Edge Cases**:
- What happens when an unauthorized origin tries to call the API? → CORS policy blocks the request at browser level
- What happens when a JWT token is tampered with? → Backend signature verification fails, returns 401 Unauthorized
- What happens when a user tries to inject SQL via task title? → SQLModel ORM parameterizes queries, injection prevented
- What happens when a user tries to inject XSS via task description? → React automatically escapes HTML, XSS prevented

## Requirements

### Functional Requirements

**Authentication & Authorization**:

- **FR-001**: System MUST allow new users to sign up with email and password
- **FR-002**: System MUST validate email format is RFC 5322 compliant (name@domain.com)
- **FR-003**: System MUST enforce password minimum length of 8 characters
- **FR-004**: System MUST hash all passwords with bcrypt before storage (Better Auth handles)
- **FR-005**: System MUST allow existing users to sign in with email and password
- **FR-006**: System MUST generate JWT token on successful authentication (Better Auth handles)
- **FR-007**: System MUST store JWT token in httpOnly cookie (Better Auth handles)
- **FR-008**: System MUST set JWT token expiration to 7 days (configurable)
- **FR-009**: System MUST allow authenticated users to sign out (clear JWT token)
- **FR-010**: System MUST redirect unauthenticated users accessing /dashboard to signin page
- **FR-011**: System MUST preserve user session across browser close/reopen within token expiry period
- **FR-012**: System MUST verify JWT token signature on all protected API endpoints
- **FR-013**: System MUST extract user_id from JWT token payload (sub claim)
- **FR-014**: System MUST verify user_id in API path matches user_id from JWT token
- **FR-015**: System MUST return 401 Unauthorized for invalid or expired tokens
- **FR-016**: System MUST return 403 Forbidden when user_id mismatch detected

**Task CRUD Operations**:

- **FR-017**: System MUST allow authenticated users to create tasks with title (1-200 characters, required)
- **FR-018**: System MUST allow authenticated users to create tasks with optional description (0-1000 characters)
- **FR-019**: System MUST associate each task with the authenticated user's user_id
- **FR-020**: System MUST auto-generate unique task ID using database SERIAL auto-increment
- **FR-021**: System MUST set new tasks with completed=false by default
- **FR-022**: System MUST auto-generate created_at timestamp on task creation
- **FR-023**: System MUST auto-generate updated_at timestamp on task creation
- **FR-024**: System MUST allow authenticated users to view all their tasks
- **FR-025**: System MUST filter tasks by user_id (WHERE user_id = token.user_id)
- **FR-026**: System MUST return tasks sorted by created_at DESC (newest first)
- **FR-027**: System MUST allow authenticated users to edit task title and/or description
- **FR-028**: System MUST update updated_at timestamp automatically on task edit
- **FR-029**: System MUST allow authenticated users to delete their tasks
- **FR-030**: System MUST allow authenticated users to toggle task completion status
- **FR-031**: System MUST prevent users from accessing, editing, deleting, or toggling other users' tasks

**Data Persistence**:

- **FR-032**: System MUST persist all user data in Neon PostgreSQL database
- **FR-033**: System MUST persist all task data in Neon PostgreSQL database
- **FR-034**: System MUST ensure data survives server restarts
- **FR-035**: System MUST ensure data survives browser close/reopen
- **FR-036**: System MUST use SQLModel ORM for all database operations (no raw SQL)
- **FR-037**: System MUST enable database connection pooling
- **FR-038**: System MUST enforce foreign key constraint: tasks.user_id → users.id
- **FR-039**: System MUST cascade delete tasks when user is deleted

**API Endpoints**:

- **FR-040**: System MUST provide POST /api/auth/signup endpoint (Better Auth)
- **FR-041**: System MUST provide POST /api/auth/signin endpoint (Better Auth)
- **FR-042**: System MUST provide POST /api/auth/signout endpoint (Better Auth)
- **FR-043**: System MUST provide GET /api/{user_id}/tasks endpoint (list tasks)
- **FR-044**: System MUST provide POST /api/{user_id}/tasks endpoint (create task)
- **FR-045**: System MUST provide GET /api/{user_id}/tasks/{id} endpoint (get task details)
- **FR-046**: System MUST provide PUT /api/{user_id}/tasks/{id} endpoint (update task)
- **FR-047**: System MUST provide DELETE /api/{user_id}/tasks/{id} endpoint (delete task)
- **FR-048**: System MUST provide PATCH /api/{user_id}/tasks/{id}/complete endpoint (toggle status)
- **FR-049**: All task endpoints MUST require valid JWT token in Authorization: Bearer <token> header
- **FR-050**: All task endpoints MUST return 401 if JWT token invalid or missing
- **FR-051**: All task endpoints MUST return 403 if user_id mismatch

**Validation**:

- **FR-052**: System MUST validate task title not empty after trim
- **FR-053**: System MUST validate task title length ≤200 characters
- **FR-054**: System MUST validate task description length ≤1000 characters (if provided)
- **FR-055**: System MUST perform validation on frontend (client-side) for immediate feedback
- **FR-056**: System MUST perform validation on backend (server-side) as security boundary
- **FR-057**: System MUST return 422 Unprocessable Entity for validation errors
- **FR-058**: System MUST return descriptive error messages for validation failures

**Frontend Pages**:

- **FR-059**: System MUST provide landing/signin page at / (public route)
- **FR-060**: System MUST provide signup page at /signup (public route)
- **FR-061**: System MUST provide dashboard page at /dashboard (protected route)
- **FR-062**: System MUST display user email and sign out button in dashboard header
- **FR-063**: System MUST display "Add New Task" form on dashboard
- **FR-064**: System MUST display list of user's tasks on dashboard
- **FR-065**: System MUST display empty state when user has no tasks
- **FR-066**: System MUST display character counters for title (X/200) and description (X/1000)
- **FR-067**: System MUST display loading states during async operations
- **FR-068**: System MUST display success toast notifications after successful actions
- **FR-069**: System MUST display error toast notifications on failures
- **FR-070**: System MUST display inline validation errors below form fields

**UI/UX Requirements**:

- **FR-071**: System MUST implement responsive design working on mobile (320px+), tablet (768px+), and desktop (1024px+)
- **FR-072**: System MUST use Tailwind CSS utility classes exclusively for styling
- **FR-073**: System MUST implement mobile-first responsive approach
- **FR-074**: System MUST show loading spinners on buttons during async operations
- **FR-075**: System MUST disable submit buttons during async operations to prevent duplicates
- **FR-076**: System MUST clear form inputs after successful task creation
- **FR-077**: System MUST show confirmation dialog before task deletion
- **FR-078**: System MUST implement optimistic UI updates for status toggle
- **FR-079**: System MUST revert optimistic updates on API failure

### Key Entities

**User** (Managed by Better Auth):
- Represents an individual user account with authentication credentials
- Attributes: id (UUID), email (unique), name, password_hash, created_at
- Relationships: One user has many tasks (1:N)
- Constraints: Email must be unique and valid format

**Task**:
- Represents a todo item belonging to a specific user
- Attributes: id (auto-increment), user_id (foreign key), title, description (optional), completed (boolean), created_at, updated_at
- Relationships: Each task belongs to one user (N:1)
- Constraints: user_id must reference valid user, title length 1-200 chars, description max 1000 chars
- Lifecycle: Created → (Optionally Edited) → (Optionally Completed/Uncompleted) → (Optionally Deleted)

## Success Criteria

### Measurable Outcomes

**Functional Success**:

- **SC-001**: 100% of users can successfully create an account with valid credentials (email + password ≥8 chars)
- **SC-002**: 100% of users can successfully sign in with correct credentials within 3 seconds
- **SC-003**: 100% of authenticated users can create a task and see it immediately in their task list within 2 seconds
- **SC-004**: 100% of authenticated users can view only their own tasks (user isolation verified with 2+ test accounts)
- **SC-005**: 100% of task CRUD operations (Create, Read, Update, Delete, Toggle) work correctly and persist to database
- **SC-006**: 100% of validation rules are enforced (title 1-200 chars, description ≤1000 chars)
- **SC-007**: 100% of error scenarios display user-friendly error messages

**Technical Success**:

- **SC-008**: Frontend TypeScript strict mode compiles with zero errors
- **SC-009**: Backend Python type hints pass type checking (mypy or similar)
- **SC-010**: All API endpoints return proper HTTP status codes (200, 201, 204, 400, 401, 403, 404, 422, 500)
- **SC-011**: JWT tokens are verified on 100% of protected endpoints
- **SC-012**: User isolation is enforced on 100% of task operations (verified with automated tests)
- **SC-013**: Zero raw SQL queries in codebase (100% SQLModel ORM usage)
- **SC-014**: Zero console errors in browser during normal operation
- **SC-015**: Zero unhandled promise rejections

**Performance Success**:

- **SC-016**: Frontend initial page load completes in <2 seconds on 3G connection
- **SC-017**: API response time (P95) is <500ms for all endpoints
- **SC-018**: Database queries execute in <100ms
- **SC-019**: Dashboard displays tasks within 1 second of page load

**Security Success**:

- **SC-020**: 100% of passwords are hashed with bcrypt (verified by database inspection)
- **SC-021**: JWT tokens are stored exclusively in httpOnly cookies (not localStorage or sessionStorage)
- **SC-022**: SQL injection is prevented on 100% of database operations (automated security scan)
- **SC-023**: XSS is prevented on 100% of user-generated content (automated security scan)
- **SC-024**: CORS is configured to allow only the frontend origin

**User Experience Success**:

- **SC-025**: 90% of users can successfully create their first task within 2 minutes of signing up (measured via user testing)
- **SC-026**: Empty state provides clear guidance for users with no tasks
- **SC-027**: All forms provide inline validation feedback within 500ms of user input
- **SC-028**: All async operations show loading states (no "dead click" experiences)
- **SC-029**: Application is usable on mobile devices with viewport width ≥320px
- **SC-030**: Application is deployed to Vercel with publicly accessible URL

**Data Integrity Success**:

- **SC-031**: Tasks persist after browser close and reopen (100% persistence verified)
- **SC-032**: Tasks persist after server restart (100% persistence verified)
- **SC-033**: User sessions persist for 7 days without requiring re-authentication
- **SC-034**: Cascade deletion works correctly (user deleted → all their tasks deleted)
- **SC-035**: Foreign key constraints prevent orphaned tasks (no tasks with invalid user_id)

## Data Requirements

### Database Schema

**users Table** (Managed by Better Auth):

```
Table: users
Columns:
  - id: VARCHAR (or UUID) - Primary Key
  - email: VARCHAR - Unique, Not Null, Indexed
  - name: VARCHAR - Nullable
  - password_hash: VARCHAR - Not Null
  - created_at: TIMESTAMP - Default NOW()

Indexes:
  - PRIMARY KEY (id)
  - UNIQUE INDEX (email)
```

**tasks Table**:

```
Table: tasks
Columns:
  - id: SERIAL - Primary Key, Auto-increment
  - user_id: VARCHAR - Foreign Key → users.id, Not Null, Indexed
  - title: VARCHAR(200) - Not Null
  - description: TEXT - Nullable
  - completed: BOOLEAN - Default false, Not Null
  - created_at: TIMESTAMP - Default NOW(), Not Null
  - updated_at: TIMESTAMP - Default NOW(), Not Null, Auto-update on change

Constraints:
  - FOREIGN KEY user_id REFERENCES users(id) ON DELETE CASCADE
  - CHECK (char_length(title) >= 1 AND char_length(title) <= 200)
  - CHECK (description IS NULL OR char_length(description) <= 1000)

Indexes:
  - PRIMARY KEY (id)
  - INDEX (user_id) - For filtering tasks by user
  - INDEX (user_id, created_at DESC) - For sorted task queries
```

### Entity Relationships

```
User (1) ──< (N) Task

- One user has many tasks (1:N)
- Each task belongs to one user (N:1)
- Cascade delete: User deleted → All their tasks deleted
- Referential integrity enforced by database foreign key constraint
```

### Data Validation Rules

**User Data**:
- Email: RFC 5322 compliant, unique in database
- Password: Minimum 8 characters (enforced at signup)
- password_hash: Bcrypt hash with cost factor ≥10 (Better Auth handles)

**Task Data**:
- title: 1-200 characters, required, non-empty after trim
- description: 0-1000 characters, optional
- completed: Boolean (true/false), defaults to false
- user_id: Must reference existing user in users table
- created_at: Auto-generated on creation, immutable
- updated_at: Auto-generated on creation, auto-updated on edit/toggle

## API Specifications

### Authentication Endpoints (Better Auth)

**POST /api/auth/signup**
- **Purpose**: Create new user account
- **Request Body**: `{"email": "john@example.com", "password": "SecurePass123", "name": "John Doe"}`
- **Success Response**: 201 Created, JWT token set in httpOnly cookie, returns user object
- **Error Responses**:
  - 400 Bad Request: Invalid email format
  - 422 Unprocessable Entity: Password too short, email already exists
  - 500 Internal Server Error: Database error

**POST /api/auth/signin**
- **Purpose**: Authenticate existing user
- **Request Body**: `{"email": "john@example.com", "password": "SecurePass123"}`
- **Success Response**: 200 OK, JWT token set in httpOnly cookie, returns user object
- **Error Responses**:
  - 401 Unauthorized: Invalid credentials (generic message for security)
  - 500 Internal Server Error: Authentication service error

**POST /api/auth/signout**
- **Purpose**: End user session
- **Request Body**: Empty
- **Success Response**: 200 OK, JWT token cleared from cookie
- **Error Responses**: None expected

### Task Endpoints (Custom FastAPI)

**GET /api/{user_id}/tasks**
- **Purpose**: List all authenticated user's tasks
- **Authentication**: Required (JWT in Authorization: Bearer <token>)
- **Path Parameters**: user_id (must match token user_id)
- **Query Parameters**: None in Phase 2 (filtering/pagination future)
- **Success Response**: 200 OK, returns array of task objects sorted by created_at DESC
- **Example Response**:
  ```json
  [
    {
      "id": 3,
      "user_id": "user-uuid-123",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2025-12-30T10:30:00Z",
      "updated_at": "2025-12-30T10:30:00Z"
    },
    {
      "id": 2,
      "user_id": "user-uuid-123",
      "title": "Finish hackathon",
      "description": null,
      "completed": true,
      "created_at": "2025-12-29T15:20:00Z",
      "updated_at": "2025-12-30T09:15:00Z"
    }
  ]
  ```
- **Error Responses**:
  - 401 Unauthorized: Invalid/missing JWT token
  - 403 Forbidden: user_id in path doesn't match token user_id
  - 500 Internal Server Error: Database query error

**POST /api/{user_id}/tasks**
- **Purpose**: Create new task for authenticated user
- **Authentication**: Required (JWT in Authorization: Bearer <token>)
- **Path Parameters**: user_id (must match token user_id)
- **Request Body**: `{"title": "Buy groceries", "description": "Milk, eggs, bread"}`
  - title: Required, 1-200 characters
  - description: Optional, max 1000 characters
- **Success Response**: 201 Created, returns created task object with generated id and timestamps
- **Example Response**:
  ```json
  {
    "id": 4,
    "user_id": "user-uuid-123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-31T12:00:00Z",
    "updated_at": "2025-12-31T12:00:00Z"
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Invalid JSON format
  - 401 Unauthorized: Invalid/missing JWT token
  - 403 Forbidden: user_id mismatch
  - 422 Unprocessable Entity: Validation errors (empty title, title too long, description too long)
  - 500 Internal Server Error: Database insert error

**GET /api/{user_id}/tasks/{id}**
- **Purpose**: Get specific task details
- **Authentication**: Required (JWT in Authorization: Bearer <token>)
- **Path Parameters**: user_id (must match token user_id), id (task ID)
- **Success Response**: 200 OK, returns task object
- **Error Responses**:
  - 401 Unauthorized: Invalid/missing JWT token
  - 403 Forbidden: user_id mismatch or task doesn't belong to user
  - 404 Not Found: Task with given id doesn't exist
  - 500 Internal Server Error: Database query error

**PUT /api/{user_id}/tasks/{id}**
- **Purpose**: Update existing task title and/or description
- **Authentication**: Required (JWT in Authorization: Bearer <token>)
- **Path Parameters**: user_id (must match token user_id), id (task ID)
- **Request Body**: `{"title": "Buy groceries and fruits", "description": "Milk, eggs, bread, apples"}`
  - title: Required, 1-200 characters
  - description: Optional, max 1000 characters
- **Success Response**: 200 OK, returns updated task object with new updated_at timestamp
- **Error Responses**:
  - 400 Bad Request: Invalid JSON format
  - 401 Unauthorized: Invalid/missing JWT token
  - 403 Forbidden: user_id mismatch or task doesn't belong to user
  - 404 Not Found: Task with given id doesn't exist
  - 422 Unprocessable Entity: Validation errors
  - 500 Internal Server Error: Database update error

**DELETE /api/{user_id}/tasks/{id}**
- **Purpose**: Permanently delete task
- **Authentication**: Required (JWT in Authorization: Bearer <token>)
- **Path Parameters**: user_id (must match token user_id), id (task ID)
- **Request Body**: Empty
- **Success Response**: 204 No Content (empty response body)
- **Error Responses**:
  - 401 Unauthorized: Invalid/missing JWT token
  - 403 Forbidden: user_id mismatch or task doesn't belong to user
  - 404 Not Found: Task with given id doesn't exist
  - 500 Internal Server Error: Database delete error

**PATCH /api/{user_id}/tasks/{id}/complete**
- **Purpose**: Toggle task completion status (true ↔ false)
- **Authentication**: Required (JWT in Authorization: Bearer <token>)
- **Path Parameters**: user_id (must match token user_id), id (task ID)
- **Request Body**: Empty (toggle action)
- **Success Response**: 200 OK, returns updated task object with toggled completed status and new updated_at
- **Example**: If task.completed was false, it becomes true (and vice versa)
- **Error Responses**:
  - 401 Unauthorized: Invalid/missing JWT token
  - 403 Forbidden: user_id mismatch or task doesn't belong to user
  - 404 Not Found: Task with given id doesn't exist
  - 500 Internal Server Error: Database update error

## Error Handling

### Frontend Error Display Strategy

**Validation Errors** (Client-side):
- Display inline below form field
- Red text color (text-red-600)
- Red border on invalid field (border-red-500)
- Show character counter when approaching limit
- Example: "Title must be 200 characters or less (currently: 205)"

**API Errors** (Server-side):
- Display toast notifications (top-right or bottom-center)
- Auto-dismiss after 5 seconds (or manual dismiss)
- Color-coded: red for errors, green for success
- Examples:
  - 401: Redirect to signin with message "Session expired. Please sign in."
  - 404: Toast "This task no longer exists"
  - 422: Inline validation messages below fields
  - 500: Toast "Something went wrong. Please try again."

**Network Errors**:
- Display toast notification with retry option
- Example: "Unable to connect. Check your internet connection. [Retry]"
- Preserve form data so user doesn't lose input

**Loading States**:
- Disable submit buttons during async operations
- Show spinner icon on buttons
- Show loading skeletons for content being fetched
- Prevent duplicate submissions

### Backend Error Response Format

All error responses follow consistent JSON format:

```json
{
  "detail": "Error message here"
}
```

**For validation errors (422)**:
```json
{
  "detail": {
    "title": "Title must be 200 characters or less",
    "description": "Description must be 1000 characters or less"
  }
}
```

### User-Friendly Error Messages

**Validation Errors**:
- Empty title: "Title is required"
- Title too long: "Title must be 200 characters or less (currently: {count})"
- Description too long: "Description must be 1000 characters or less (currently: {count})"
- Invalid email: "Please enter a valid email address"
- Weak password: "Password must be at least 8 characters"
- Passwords don't match: "Passwords must match"

**Authentication Errors**:
- Email exists: "This email is already registered. Try signing in."
- Invalid credentials: "Invalid email or password" (generic for security)
- Session expired: "Session expired. Please sign in again."

**Authorization Errors**:
- Access denied: "You don't have permission to perform this action"

**Resource Errors**:
- Task not found: "This task no longer exists"
- Not found: "Resource not found"

**Network Errors**:
- Connection failed: "Unable to connect. Check your internet connection."
- Timeout: "Request timed out. Please try again."

**Server Errors**:
- Generic: "Something went wrong. Please try again later."
- Database error: "Unable to save changes. Please try again."

## Out of Scope (Phase 2)

The following features are explicitly excluded from Phase 2 and will not be implemented:

**Advanced Task Features**:
- Task priorities (low, medium, high)
- Task tags or categories
- Task due dates and deadlines
- Task reminders and notifications
- Recurring tasks
- Subtasks or nested tasks
- Task attachments or file uploads
- Task comments or notes
- Task collaboration or sharing between users
- Task archiving
- Bulk operations (delete multiple tasks at once)
- Drag-and-drop task reordering
- Task export (CSV, JSON)
- Task import

**Search and Filtering**:
- Task search by keyword
- Filter tasks by status (completed/pending)
- Filter by date range
- Sort options (by title, date, priority, etc.)

**Authentication Advanced Features**:
- Email verification
- Password reset flow
- Two-factor authentication (2FA)
- Social login (Google, GitHub, etc.)
- Remember me option
- Account deletion

**User Profile and Settings**:
- User profile page
- Edit profile (name, email)
- Change password
- User settings/preferences
- Avatar upload

**UI/UX Enhancements**:
- Dark mode toggle
- Theme customization
- Keyboard shortcuts
- Accessibility audit (WCAG compliance)
- Internationalization (i18n)
- Onboarding tutorial

**Real-time and Offline**:
- Real-time sync between devices (WebSockets/SSE)
- Offline support (PWA)
- Background sync

**Infrastructure and Monitoring**:
- API rate limiting
- API versioning (v1, v2, etc.)
- Comprehensive logging system
- Analytics and metrics
- Performance monitoring
- Error tracking (Sentry, etc.)
- Email notifications
- Admin dashboard
- User management panel

**Testing and CI/CD**:
- Comprehensive unit tests
- Integration tests
- End-to-end tests
- CI/CD pipeline
- Automated deployments

**Mobile**:
- Mobile native app (iOS/Android)
- Desktop app (Electron)
- Browser extension

## Technology Stack (from Constitution)

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth (client)
- **State**: React hooks (useState, useEffect, useCallback, useMemo)
- **HTTP Client**: Fetch API (built-in)
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI (async/await)
- **Language**: Python 3.13+ (type hints)
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT verification (shared secret with Better Auth)
- **Validation**: Pydantic models

### Development Tools
- **Package Managers**: npm (frontend), pip/uv (backend)
- **Environment Files**: .env.local (frontend), .env (backend)
- **Version Control**: Git + GitHub

## Security Requirements (from Constitution)

**Authentication Security**:
- Passwords hashed with bcrypt (cost factor ≥10)
- JWT tokens signed with HS256 algorithm
- Secret key minimum 32 characters
- Token expiration enforced (7 days)
- httpOnly cookies (not accessible via JavaScript)
- Secure flag in production (HTTPS only)

**Authorization Security**:
- Every task endpoint validates JWT
- user_id extracted from token (sub claim)
- user_id in path must match token user_id
- Database queries filtered by user_id
- 403 Forbidden if user_id mismatch
- 401 Unauthorized if token invalid/expired

**Input Validation**:
- Frontend validation (client-side) for UX
- Backend validation (server-side) as security boundary
- Never trust client input
- Sanitize all inputs
- Maximum length enforcement
- Type validation via Pydantic models

**Database Security**:
- No raw SQL queries (SQLModel ORM only)
- Parameterized queries (prevents SQL injection)
- Foreign key constraints enforced
- Proper indexes for performance
- Connection pooling (prevent exhaustion)

**API Security**:
- CORS restricted to frontend origin
- HTTPS in production
- No sensitive data in URLs
- No sensitive data in logs

## Performance Requirements (from Constitution)

**Frontend Performance**:
- Initial page load: <2 seconds
- Time to Interactive (TTI): <3 seconds
- First Contentful Paint (FCP): <1.5 seconds
- Largest Contentful Paint (LCP): <2.5 seconds
- Cumulative Layout Shift (CLS): <0.1
- First Input Delay (FID): <100ms
- Lighthouse Performance score: >80

**Backend Performance**:
- API response time (P50): <200ms
- API response time (P95): <500ms
- API response time (P99): <1000ms
- Database query time: <100ms
- Concurrent requests: Support 100+ simultaneous users

**Database Performance**:
- Query optimization with proper indexes
- Connection pooling (min 5, max 20 connections)
- No N+1 query problems
- Efficient WHERE clauses (indexed columns)

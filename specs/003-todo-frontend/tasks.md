# Tasks: Todo Frontend Integration

**Input**: Design documents from `/specs/003-todo-frontend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-client.md

**Tests**: Tests are explicitly out of scope per specification ("Automated testing will be addressed in separate testing phase")

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/app/`, `frontend/src/components/`, `frontend/src/lib/`, `frontend/src/types/`
- **Backend**: `backend/src/` (existing from Phase 2)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Next.js structure

- [ ] T001 Create Next.js 16+ application with TypeScript in frontend/ directory using create-next-app
- [ ] T002 Install core dependencies: better-auth, zod in frontend/package.json
- [ ] T003 [P] Create .env.local.example with NEXT_PUBLIC_API_URL and BETTER_AUTH_SECRET in frontend/
- [ ] T004 [P] Configure TypeScript strict mode in frontend/tsconfig.json
- [ ] T005 [P] Create frontend/src/app/layout.tsx root layout with metadata
- [ ] T006 [P] Create frontend/src/app/globals.css with base styles and CSS reset

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 [P] Create TypeScript type definitions in frontend/src/types/task.ts (Task, TaskCreate, TaskUpdate)
- [ ] T008 [P] Create TypeScript type definitions in frontend/src/types/api.ts (ApiError, ApiResponse, LoadingState)
- [ ] T009 [P] Create TypeScript type definitions in frontend/src/types/auth.ts (UserSession, SignUpRequest, SignInRequest, AuthResponse)
- [ ] T010 [P] Create validation rules constant in frontend/src/lib/utils/validation.ts (VALIDATION_RULES)
- [ ] T011 [P] Create API endpoints constant in frontend/src/lib/utils/constants.ts (API_ENDPOINTS, HTTP_STATUS)
- [ ] T012 Create APIError class in frontend/src/lib/api/errors.ts with statusCode, code, detail fields
- [ ] T013 Create base APIClient class in frontend/src/lib/api/client.ts with request(), get(), post(), put(), patch(), delete() methods
- [ ] T014 Implement JWT token injection in APIClient.request() method in frontend/src/lib/api/client.ts
- [ ] T015 Implement authentication error handling (401/403) in APIClient.request() in frontend/src/lib/api/client.ts
- [ ] T016 Create TaskAPI class in frontend/src/lib/api/tasks.ts with list(), get(), create(), update(), delete(), toggleComplete() methods
- [ ] T017 [P] Create Better Auth configuration in frontend/src/lib/auth/better-auth.ts
- [ ] T018 [P] Create authentication middleware in frontend/src/middleware.ts for route protection
- [ ] T019 [P] Create reusable Button component in frontend/src/components/ui/Button.tsx
- [ ] T020 [P] Create reusable Input component in frontend/src/components/ui/Input.tsx
- [ ] T021 [P] Create reusable LoadingSpinner component in frontend/src/components/ui/LoadingSpinner.tsx
- [ ] T022 [P] Create reusable Modal component in frontend/src/components/ui/Modal.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication Flow (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts, sign in, and access protected routes with JWT authentication

**Independent Test**: Visit application, sign up with email/password, sign out, sign back in, verify redirect to tasks dashboard and route protection works

### Implementation for User Story 1

- [ ] T023 [P] [US1] Create (auth) route group directory structure in frontend/src/app/(auth)/
- [ ] T024 [P] [US1] Create signup page in frontend/src/app/(auth)/signup/page.tsx
- [ ] T025 [P] [US1] Create signin page in frontend/src/app/(auth)/signin/page.tsx
- [ ] T026 [P] [US1] Create SignUpForm component in frontend/src/components/auth/SignUpForm.tsx with email and password fields
- [ ] T027 [P] [US1] Create SignInForm component in frontend/src/components/auth/SignInForm.tsx with email and password fields
- [ ] T028 [US1] Implement client-side validation in SignUpForm using VALIDATION_RULES in frontend/src/components/auth/SignUpForm.tsx
- [ ] T029 [US1] Implement client-side validation in SignInForm using VALIDATION_RULES in frontend/src/components/auth/SignInForm.tsx
- [ ] T030 [US1] Integrate Better Auth signUp() in SignUpForm component in frontend/src/components/auth/SignUpForm.tsx
- [ ] T031 [US1] Integrate Better Auth signIn() in SignInForm component in frontend/src/components/auth/SignInForm.tsx
- [ ] T032 [US1] Implement session storage (localStorage) for JWT token in frontend/src/lib/auth/session.ts
- [ ] T033 [US1] Implement redirect to /tasks after successful authentication in SignUpForm and SignInForm
- [ ] T034 [US1] Implement error message display for authentication failures in SignUpForm and SignInForm
- [ ] T035 [US1] Configure middleware to redirect unauthenticated users to /signin in frontend/src/middleware.ts
- [ ] T036 [US1] Implement JWT token expiration handling with redirect to /signin?expired=true in frontend/src/lib/api/client.ts
- [ ] T037 [US1] Add loading states during authentication operations in SignUpForm and SignInForm components

**Checkpoint**: At this point, User Story 1 should be fully functional - users can sign up, sign in, and access protected routes

---

## Phase 4: User Story 2 - View and Create Tasks (Priority: P2)

**Goal**: Enable authenticated users to view their task list and create new tasks

**Independent Test**: Sign in, view empty task list with empty state message, create several tasks, verify they appear in the list with title, description, and completion status

### Implementation for User Story 2

- [ ] T038 [P] [US2] Create (dashboard) route group directory structure in frontend/src/app/(dashboard)/
- [ ] T039 [US2] Create tasks page in frontend/src/app/(dashboard)/tasks/page.tsx
- [ ] T040 [P] [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx to display array of tasks
- [ ] T041 [P] [US2] Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx to display individual task
- [ ] T042 [P] [US2] Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx with title and description fields
- [ ] T043 [US2] Implement TaskAPI.list() integration in tasks page to fetch tasks on mount in frontend/src/app/(dashboard)/tasks/page.tsx
- [ ] T044 [US2] Implement TaskAPI.create() integration in TaskForm component in frontend/src/components/tasks/TaskForm.tsx
- [ ] T045 [US2] Implement client-side validation in TaskForm using VALIDATION_RULES in frontend/src/components/tasks/TaskForm.tsx
- [ ] T046 [US2] Implement empty state message when user has no tasks in TaskList component in frontend/src/components/tasks/TaskList.tsx
- [ ] T047 [US2] Implement loading state during task list fetch in tasks page in frontend/src/app/(dashboard)/tasks/page.tsx
- [ ] T048 [US2] Implement loading state during task creation in TaskForm component in frontend/src/components/tasks/TaskForm.tsx
- [ ] T049 [US2] Implement error message display for task creation failures in TaskForm component in frontend/src/components/tasks/TaskForm.tsx
- [ ] T050 [US2] Implement error message display for task list fetch failures in tasks page in frontend/src/app/(dashboard)/tasks/page.tsx
- [ ] T051 [US2] Update task list immediately after successful task creation in tasks page in frontend/src/app/(dashboard)/tasks/page.tsx
- [ ] T052 [US2] Display task title, description, and completion status in TaskItem component in frontend/src/components/tasks/TaskItem.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can authenticate and manage their task list

---

## Phase 5: User Story 3 - Update and Delete Tasks (Priority: P3)

**Goal**: Enable authenticated users to edit task details and remove tasks they no longer need

**Independent Test**: Sign in, create a task, click edit to modify title/description, save changes, then delete the task with confirmation

### Implementation for User Story 3

- [ ] T053 [P] [US3] Create TaskActions component in frontend/src/components/tasks/TaskActions.tsx with edit and delete buttons
- [ ] T054 [US3] Add edit mode state to TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [ ] T055 [US3] Implement inline edit form in TaskItem when edit mode is active in frontend/src/components/tasks/TaskItem.tsx
- [ ] T056 [US3] Implement TaskAPI.update() integration in TaskItem edit form in frontend/src/components/tasks/TaskItem.tsx
- [ ] T057 [US3] Implement client-side validation for task updates using VALIDATION_RULES in frontend/src/components/tasks/TaskItem.tsx
- [ ] T058 [US3] Implement cancel edit functionality to restore original task data in TaskItem in frontend/src/components/tasks/TaskItem.tsx
- [ ] T059 [US3] Implement delete confirmation modal using Modal component in TaskActions in frontend/src/components/tasks/TaskActions.tsx
- [ ] T060 [US3] Implement TaskAPI.delete() integration in TaskActions component in frontend/src/components/tasks/TaskActions.tsx
- [ ] T061 [US3] Update task list immediately after successful task update in tasks page in frontend/src/app/(dashboard)/tasks/page.tsx
- [ ] T062 [US3] Update task list immediately after successful task deletion in tasks page in frontend/src/app/(dashboard)/tasks/page.tsx
- [ ] T063 [US3] Implement loading state during task update in TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [ ] T064 [US3] Implement loading state during task deletion in TaskActions component in frontend/src/components/tasks/TaskActions.tsx
- [ ] T065 [US3] Implement error message display for task update failures in TaskItem in frontend/src/components/tasks/TaskItem.tsx
- [ ] T066 [US3] Implement error message display for task deletion failures in TaskActions in frontend/src/components/tasks/TaskActions.tsx

**Checkpoint**: All core task management features should now be functional - users can create, view, edit, and delete tasks

---

## Phase 6: User Story 4 - Toggle Task Completion (Priority: P3)

**Goal**: Enable authenticated users to mark tasks as complete or incomplete to track progress

**Independent Test**: Sign in, create a task, click completion checkbox to mark complete (verify visual indication), click again to mark incomplete

### Implementation for User Story 4

- [ ] T067 [US4] Add completion checkbox to TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [ ] T068 [US4] Implement TaskAPI.toggleComplete() integration on checkbox click in TaskItem in frontend/src/components/tasks/TaskItem.tsx
- [ ] T069 [US4] Add visual indication for completed tasks (strikethrough, checkmark) in TaskItem in frontend/src/components/tasks/TaskItem.tsx
- [ ] T070 [US4] Add CSS styles for completed task state in TaskItem styles in frontend/src/components/tasks/TaskItem.tsx
- [ ] T071 [US4] Update task list immediately after successful completion toggle in tasks page in frontend/src/app/(dashboard)/tasks/page.tsx
- [ ] T072 [US4] Implement optimistic UI update for completion toggle in TaskItem in frontend/src/components/tasks/TaskItem.tsx
- [ ] T073 [US4] Implement error handling and rollback for failed completion toggle in TaskItem in frontend/src/components/tasks/TaskItem.tsx

**Checkpoint**: Task completion tracking should now be fully functional with visual feedback

---

## Phase 7: User Story 5 - Session Management and Logout (Priority: P4)

**Goal**: Enable authenticated users to securely end their session and prevent access to protected routes after logout

**Independent Test**: Sign in, click logout button, verify redirect to signin page and inability to access /tasks without re-authenticating

### Implementation for User Story 5

- [ ] T074 [P] [US5] Create Header component in frontend/src/components/layout/Header.tsx with logout button
- [ ] T075 [US5] Add Header component to root layout in frontend/src/app/layout.tsx
- [ ] T076 [US5] Implement Better Auth signOut() integration in Header logout button in frontend/src/components/layout/Header.tsx
- [ ] T077 [US5] Clear JWT token from localStorage on logout in frontend/src/lib/auth/session.ts
- [ ] T078 [US5] Implement redirect to /signin after successful logout in Header component in frontend/src/components/layout/Header.tsx
- [ ] T079 [US5] Verify middleware prevents access to /tasks after logout in frontend/src/middleware.ts
- [ ] T080 [US5] Implement browser history protection (back button) after logout in frontend/src/middleware.ts

**Checkpoint**: All user stories should now be independently functional - complete authentication and task management system

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and enhance overall user experience

- [ ] T081 [P] Implement responsive design for mobile (320px-768px) across all components using CSS media queries
- [ ] T082 [P] Implement responsive design for desktop (769px-1920px) across all components using CSS media queries
- [ ] T083 [P] Add ARIA labels and semantic HTML for accessibility in all components
- [ ] T084 [P] Implement keyboard navigation support (Tab, Enter, Escape) in all interactive components
- [ ] T085 [P] Add loading spinners for all async operations taking longer than 500ms
- [ ] T086 [P] Improve error messages to be clear and actionable across all components
- [ ] T087 [P] Add network error handling with retry functionality in APIClient in frontend/src/lib/api/client.ts
- [ ] T088 [P] Create landing page in frontend/src/app/page.tsx with links to signin/signup
- [ ] T089 [P] Add favicon and metadata in frontend/src/app/layout.tsx
- [ ] T090 [P] Implement form submission prevention on double-click across all forms
- [ ] T091 [P] Add input field character limits matching backend validation (title: 200, description: 1000)
- [ ] T092 [P] Test application across different browsers (Chrome, Firefox, Safari, Edge)
- [ ] T093 [P] Verify HTTPS configuration for production deployment
- [ ] T094 Run quickstart.md validation to ensure setup instructions are accurate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P3 → P4)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 for authentication but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires US2 for task list but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Requires US2 for task list but independently testable
- **User Story 5 (P4)**: Can start after Foundational (Phase 2) - Requires US1 for authentication but independently testable

### Within Each User Story

- Foundation components before page components
- API integration after component structure
- Validation before submission
- Error handling after core functionality
- Loading states after API integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005, T006)
- All Foundational tasks marked [P] can run in parallel within their dependency groups:
  - Type definitions: T007, T008, T009, T010, T011
  - UI components: T019, T020, T021, T022
  - Auth config: T017, T018
- Within User Story 1: T023-T025 (route structure and pages), T026-T027 (form components)
- Within User Story 2: T038-T042 (route structure and components)
- Within User Story 3: T053 (TaskActions component can be built in parallel with other components)
- Within User Story 5: T074 (Header component)
- All Polish tasks marked [P] can run in parallel (T081-T094)

---

## Parallel Example: User Story 1

```bash
# Launch route structure and pages together:
Task: "Create (auth) route group directory structure in frontend/src/app/(auth)/"
Task: "Create signup page in frontend/src/app/(auth)/signup/page.tsx"
Task: "Create signin page in frontend/src/app/(auth)/signin/page.tsx"

# Launch form components together:
Task: "Create SignUpForm component in frontend/src/components/auth/SignUpForm.tsx"
Task: "Create SignInForm component in frontend/src/components/auth/SignInForm.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch route structure and components together:
Task: "Create (dashboard) route group directory structure in frontend/src/app/(dashboard)/"
Task: "Create TaskList component in frontend/src/components/tasks/TaskList.tsx"
Task: "Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx"
Task: "Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T022) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T023-T037)
4. **STOP and VALIDATE**: Test User Story 1 independently - sign up, sign in, route protection
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - Authentication!)
3. Add User Story 2 → Test independently → Deploy/Demo (Core value - Task management!)
4. Add User Story 3 → Test independently → Deploy/Demo (Enhanced task management)
5. Add User Story 4 → Test independently → Deploy/Demo (Progress tracking)
6. Add User Story 5 → Test independently → Deploy/Demo (Security enhancement)
7. Add Polish → Final refinements → Production ready
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (View/Create Tasks) - starts after US1 auth is available
   - Developer C: User Story 3 (Update/Delete Tasks) - starts after US2 task list is available
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are explicitly out of scope per specification
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend API from Phase 2 must be running for integration testing
- Environment variables must be configured before running application
- Better Auth configuration requires BETTER_AUTH_SECRET (min 32 characters)
- All API communication uses REST (no WebSockets)
- JWT tokens attached to every API request except signin/signup
- Client-side validation is for UX only - backend enforces all security rules

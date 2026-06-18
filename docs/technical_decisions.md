
# Technical Decisions

## Username not unique
- Reason: Users authenticate with email, not username
- Allows reuse after soft delete
- Trade-off: Possible duplicates in UI

## Phone number limited to 10 characters
- Reason: Application designed for French market
- Trade-off: Not compatible with international numbers

## updated_at handled by database trigger
- Reason: Ensures consistency regardless of update source
- Trade-off: Logic not visible in ORM layer

### Password validation location

## The validation of password and confirm_password is handled in the service layer rather than the schema.
- Reason: Keeps business logic centralized in the service
- Maintains consistency with other validations

- Trade-off: Validation error happens later compared to schema validation


## User roles are restricted to "passenger" and "driver".

- Reason: The application domain (carpooling) only requires these roles for end-users.
- Administrative roles (admin, moderator, supervisor) are managed internally and are not assignable through user-facing endpoints.

# Note

1. Resources should be groupped into folders
2. Each folder should contain actions available for specific resource
3. These actions should wrap models by adding application logic
4. Each method should return a tuple of result (even when empty -> NoContent for example) and http response code
5. Returned tuple must match the api specification (yml file)
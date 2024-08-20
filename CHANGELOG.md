# Changelog

## v0.1.18 (15-08-2024)

- Add padding to footer
- Fix title on Catalogue page
- Remove DOCUMENTATION_URL references

## v0.1.17 (07-08-2024)

- Added claims middleware
- Added claims backend
- Added OPA claims middleware
- Removed django-webpack-loader
- Optimised Dockerfile
- Added `manage.py init` script to create a placeholder web presence

## v0.1.16 (05-08-2024)

- Update resource catalogue

## v0.1.15 (23-07-2024)

- Add authZ integration

## v0.1.14 (23-07-2024))

- Bugfixes:
  - Update menu hover colours
  - Fix search with spaces

## v0.1.12 (05-07-2024)

- Update website design
- Add help pages

## v0.1.11 (26-06-2024)

- Serve the wagtail media files using S3
- Add scripts for database importing/exporting

## v0.1.10 (21-05-2024)

- Add caching
- Addition of robots.txt and headers
- Add `docker-compose.yaml` configuration
- Implemented `gevent` worker class and increased number of workers to 4
- Integrated `django-webpack-loader` for static builds
- Enabled static file compilation for webpack

## v0.1.9 (10-05-2024)

- Implement design

## v0.1.8 (26-04-2024)

- Update package versions

## v0.1.7 (04-04-2024)

- Reference following from external sources:
  - SECRET_KEY
  - WAGTAIL_BASE_URL
  - ALLOWED_HOSTS

## v0.1.6 (02-04-2024)

- Fix issues with static files

## v0.1.5 (26-03-2024)

- Turn off debug mode

## v0.1.4 (19-03-2024)

- Increment version number

## v0.1.3 (19-03-2024)

- Change resource catalogue home page link to hosted S3 bucket

## v0.1.2 (05-03-2024)

- Change resource catalogue home page link to be external rather than embedded

## v0.1.1 (28-02-2024)

- Updated to use environment variables for home page and resource catalogue

## v0.1.0 (07-02-2024)

- Initial website structure:
  - home page including links to:
    - static catalogue browser (external)
    - notebooks (placeholder)
    - resource catalogue
    - eoxviewserver (external)
    - help pages
  - resource catalogue page (placeholder)
- Dockerfile
- GitHub actions

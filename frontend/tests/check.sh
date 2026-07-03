#!/bin/bash

npx prettier --write ..

npm --prefix .. test

npx playwright test --config=../playwright.config.js
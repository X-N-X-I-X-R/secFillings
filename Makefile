# Makefile לניהול פרויקט Node.js

# התקנת כל החבילות המוגדרות ב-package.json
install:
	npm install

# עדכון החבילות לגרסאות התואמות להגדרות ב-package.json
update:
	npm update

# הצגת חבילות מיושנות שניתן לעדכן
outdated:
	npm outdated

# ביצוע בדיקת אבטחה על החבילות המותקנות
audit:
	npm audit

# ניסיון לתקן בעיות אבטחה באופן אוטומטי
audit-fix:
	npm audit fix

# הפעלת האפליקציה
start:
	npm start
start-x:
	npx expo start
# בניית האפליקציה (אם יש סקריפט build)
build:
	npm run build

# הרצת בדיקות
test:
	npm test

# מחיקת תיקיית node_modules
clean:
	rm -rf node_modules

# הסרת והתקנה מחדש של החבילות
reinstall: clean install

# פקודות tree

# הצגת מבנה התיקיות והקבצים
tree:
	tree

# הצגת המבנה תוך התעלמות מתיקיית node_modules
tree-ignore:
	tree -I 'node_modules'

# הצגת המבנה תוך התעלמות ממספר תיקיות (node_modules, .git, dist)
tree-ignore-all:
	tree -I 'node_modules|.git|dist'

# הצגת המבנה עד רמה 2
tree-limited:
	tree -L 2

# הצגת קבצים עם סיומת .js בלבד
tree-js:
	tree -P '*.js'

# הצגת מבנה התיקיות בלבד (ללא קבצים)
tree-dirs:
	tree -d

# הצגת קבצים ותיקיות מוסתרים (המתחילים בנקודה)
tree-hidden:
	tree -a

# הצגת גודל הקבצים בפורמט קריא לאדם
tree-size:
	tree -h

# שמירת המבנה לקובץ tree.txt
tree-save:
	tree > tree.txt
findnopath:
	find . -not -path "./node_modules/*"
# הגדרת מטרות שאינן קבצים (phony targets)
.PHONY: install update outdated audit audit-fix start build test clean reinstall \
        tree tree-ignore tree-ignore-all tree-limited tree-js tree-dirs tree-hidden \
        tree-size tree-save



### 📱 Expo Boilerplate Project

This repository contains a **simple and efficient Expo boilerplate** designed to streamline the development process for future projects. 

#### 🚀 Features:
- **Quick Setup:** Pre-configured Expo environment to get started instantly.
- **Customizable Structure:** Minimalistic and flexible, suitable for a variety of app types.
- **Scalable Codebase:** Easily extendable for larger, more complex projects.

#### 🛠️ Usage:
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/expo-boilerplate.git
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm start
   ```
4. Customize and build your app!

#### 🌟 Why use this boilerplate?
- Saves time when starting new projects.
- Encourages consistent structure across different apps.
- Compatible with the latest Expo SDK and tools.

Feel free to contribute, open issues, or submit pull requests! 😊

---
# ExpoBoilerplate

הנה שלבים ברורים להקמת פרויקט חדש מבוסס על הבוילרפלייט :
---

### 1. **שכפול פרויקט הבוילרפלייט**
כדי לוודא שהפרויקט המהיר נשאר נקי משינויים, תוכל לשכפל אותו לפרויקט חדש:
1. **צור תיקיית פרויקט חדשה**:
   ```bash
   mkdir my-new-project
   cd my-new-project
   ```

2. **שכפול הפרויקט המהיר**:
   השתמש בפקודה `git clone`:
   ```bash
   git clone https://github.com/your-username/expo-boilerplate.git .
   ```
   הוספת הנקודה (`.`) בסוף הפקודה תעתיק את כל התוכן של הפרויקט לתיקייה החדשה.

---

### 2. **התאמת הפרויקט החדש**
לאחר ששכפלת את הפרויקט, בצע את השינויים הבאים:

#### א. **שינוי המזהה והשם של הפרויקט**
1. ערוך את הקובץ `app.json` ושנה את המזהה (slug) והשם:
   ```json
   {
     "expo": {
       "name": "My New Project",
       "slug": "my-new-project",
       ...
     }
   }
   ```

2. ודא שהמזהה `slug` ייחודי כדי להימנע מהתנגשויות בשימוש בכלים של Expo.

---

### 3. **ניהול גיט לפרויקט החדש**
כדי לוודא שהפרויקט החדש יישמר בנפרד בגיט, בצע את הפעולות הבאות:

1. **מחק את הקבצים הקשורים לפרויקט הקודם בגיט**:
   ```bash
   rm -rf .git
   ```

2. **אתחל מחדש את גיט בפרויקט**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for My New Project"
   ```

3. **צור מאגר חדש ב-GitHub לפרויקט החדש**, והוסף אותו כ-remote:
   ```bash
   git remote add origin https://github.com/your-username/my-new-project.git
   git push -u origin main
   ```

---

### 4. **התחל פיתוח הפרויקט**
עכשיו אתה מוכן להתחיל את הפיתוח של הפרויקט האמיתי! תוכל:
- להתקין חבילות נוספות:
  ```bash
  npm install [package-name]
  ```
- להתחיל לכתוב את הקוד החדש בתיקיית `src`.

---

### 5. **עדכן את התיעוד**
בפרויקט החדש, עדכן את הקובץ `README.md` שיתאר את מטרת הפרויקט החדש שלך. ניתן להשתמש בתבנית קודמת עם התאמות ייעודיות לפרויקט הזה.

---

### 6. **הרץ את האפליקציה**
וודא שהכל עובד:
```bash
npm start
```
בדוק את האפליקציה על האמולטור או על מכשיר פיזי.

---


from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, TextAreaField, DecimalField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Email, Length, Regexp, NumberRange


class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я",
        validators=[
            DataRequired(message="Ім'я є обов'язковим для заповнення"),
            Length(min=4, max=10, message="Довжина імені повинна бути від 4 до 10 символів")
        ]
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email є обов'язковим для заповнення"),
            Email(message="Введіть коректну адресу електронної пошти")
        ]
    )
    phone = StringField(
        "Телефон",
        validators=[
            DataRequired(message="Телефон є обов'язковим для заповнення"),
            Regexp(r"^\+380\d{9}$", message="Номер телефону повинен бути у форматі +380XXXXXXXXX")
        ]
    )
    subject = SelectField(
        "Тема повідомлення",
        choices=[
            ("", "Оберіть тему..."),
            ("collaboration", "Співпраця"),
            ("support", "Технічна підтримка"),
            ("question", "Запитання"),
            ("feedback", "Відгук")
        ],
        validators=[
            DataRequired(message="Будь ласка, оберіть тему повідомлення")
        ]
    )
    message = TextAreaField(
        "Повідомлення",
        validators=[
            DataRequired(message="Повідомлення є обов'язковим для заповнення"),
            Length(max=500, message="Довжина повідомлення не повинна перевищувати 500 символів")
        ],
        render_kw={"rows": 5, "placeholder": "Введіть ваше повідомлення..."}
    )
    submit = SubmitField("Send Message")


PRODUCT_CATEGORIES = [
    ("", "Оберіть категорію..."),
    ("electronics", "Електроніка"),
    ("clothing", "Одяг"),
    ("books", "Книги"),
    ("home", "Товари для дому"),
    ("sports", "Спорт і відпочинок")
]


class ProductForm(FlaskForm):
    name = StringField(
        "Назва товару",
        validators=[
            DataRequired(message="Назва товару є обов'язковою"),
            Length(min=3, message="Назва повинна містити щонайменше 3 символи")
        ]
    )
    content = TextAreaField(
        "Опис товару",
        validators=[
            DataRequired(message="Опис товару є обов'язковим")
        ],
        render_kw={"rows": 5, "cols": 40, "placeholder": "Введіть детальний опис товару..."}
    )
    price = DecimalField(
        "Ціна (грн)",
        places=2,
        validators=[
            InputRequired(message="Ціна є обов'язковою"),
            NumberRange(min=0.01, message="Ціна повинна бути додатнім числом")
        ]
    )
    category = SelectField(
        "Категорія",
        choices=PRODUCT_CATEGORIES,
        validators=[
            DataRequired(message="Оберіть категорію товару")
        ]
    )
    quantity = IntegerField(
        "Кількість одиниць",
        validators=[
            InputRequired(message="Кількість є обов'язковою"),
            NumberRange(min=0, message="Кількість повинна бути невід'ємним цілим числом (0 або більше)")
        ]
    )
    image = FileField(
        "Зображення товару",
        validators=[
            FileAllowed(["png", "jpg", "jpeg"], message="Підтримуються лише формати PNG, JPG та JPEG"),
            FileSize(max_size=5 * 1024 * 1024, message="Розмір файлу не повинен перевищувати 5 MB")
        ]
    )
    submit = SubmitField("Зберегти")

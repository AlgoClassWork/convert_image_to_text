from django.shortcuts import render, redirect
from .models import UploadedImage
import easyocr
import io

# Создаем "читалку" один раз. Это важно для производительности,
# чтобы не загружать модели при каждом запросе.
# Указываем, что нам нужны русский и английский языки.
reader = easyocr.Reader(['ru', 'en'])

def upload_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        if not image_file:
            return render(request, 'converter/upload.html', {'error': 'Файл не выбран!'})

        # Создаем объект в базе данных
        uploaded_image = UploadedImage.objects.create(image=image_file)

        try:
            # Получаем путь к сохраненному файлу
            image_path = uploaded_image.image.path
            
            # Распознаем текст с помощью EasyOCR
            # readtext возвращает список кортежей: (bbox, text, confidence)
            result = reader.readtext(image_path)

            # Собираем весь распознанный текст в одну строку
            extracted_text_list = [text for bbox, text, confidence in result]
            extracted_text = '\n'.join(extracted_text_list)
            
            # Сохраняем текст в нашу модель
            uploaded_image.text = extracted_text
            uploaded_image.save()
            
            # Перенаправляем на страницу с результатом
            return redirect('result', pk=uploaded_image.pk)
            
        except Exception as e:
            # Ловим возможные ошибки
            return render(request, 'converter/upload.html', {'error': f'Произошла ошибка: {e}'})

    # Если это GET-запрос, просто показываем страницу загрузки
    return render(request, 'converter/upload.html')


def show_result(request, pk):
    try:
        uploaded_image = UploadedImage.objects.get(pk=pk)
        context = {
            'image_url': uploaded_image.image.url,
            'text': uploaded_image.text
        }
        return render(request, 'converter/result.html', context)
    except UploadedImage.DoesNotExist:
        return redirect('upload_image')
FROM public.ecr.aws/lambda/python:3.12-arm64

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ${LAMBDA_TASK_ROOT}/app/

CMD ["app.main.handler"]

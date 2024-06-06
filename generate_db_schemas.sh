APPS=("users" "completions" "groups" "organizations" "questions")

mkdir -p docs/db_schemas

for APP in "${APPS[@]}"
do
   echo "$APP"
   python manage.py graph_models "$APP" --hide-edge-labels -o docs/db_schemas/"$APP".png
done

python manage.py graph_models -a -X Session,AbstractBaseSession,AbstractBaseUser,ContentType,LogEntry --hide-edge-labels -o docs/db_schemas/full.png

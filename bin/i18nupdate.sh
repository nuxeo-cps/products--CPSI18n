#!/bin/sh

DIR=".."

echo
echo -n "CPS Products directory: "
echo $DIR
echo -n "i18ndude executable: "
echo `which i18ndude`
echo -n "Options: "
echo $@
echo

echo "################ Working on 'default' domain ###########################"

i18ndude rebuild-pot --exclude build --pot "i18n/generated-default.pot" --create default .

for file in `grep -l --exclude=*custom.pot 'Domain: default' $DIR/CPS*/i18n/*.pot`; do
  i18ndude filter "i18n/generated-default.pot" "$file" > "i18n/generated2-default.pot"
  mv "i18n/generated2-default.pot" "i18n/generated-default.pot"
done

i18ndude merge --pot "i18n/default.pot" --merge "i18n/generated-default.pot" --merge2 "i18n/manual-default.pot" 2>/dev/null

i18ndude sync --pot "i18n/default.pot" "i18n/default-fr.po" "i18n/default-en.po" 2>/dev/null

echo "################ Search for untranslated messages ####################"

i18ndude find-untranslated $@ `find skins -name "*.*pt"|sort`


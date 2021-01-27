L=$1

echo "L=${L}"
R=""
for i in ${L[@]}; do
    R=`printf "${R}\n%04d" ${i#0}`
done


echo "R=${R}"
echo ""

echo "L"
for i in ${L[@]}; do
    echo ${i}
done
echo ""

echo "R"
for i in ${R[@]}; do
    echo ${i}
done

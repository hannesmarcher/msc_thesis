for compose in $@
do
	lines_count=$(docker compose -f $compose ps | wc -l)

	for (( c=2; c<=$lines_count; c++ ))
	do
		temp="p"
		container=$(docker compose -f $compose ps | cut -d " " -f 1 | sed -n "$c$temp")

		START=$(docker inspect --format='{{.State.StartedAt}}' $container)
		STOP=$(docker inspect --format='{{.State.FinishedAt}}' $container)
		START_TIMESTAMP=$(date --date=$START +%s)
		STOP_TIMESTAMP=$(date --date=$STOP +%s)
		echo $container: $(($STOP_TIMESTAMP-$START_TIMESTAMP)) seconds
	done
done






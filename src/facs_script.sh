facs_dir='/home/arindam/Dropbox/Brunel/FACS/facs'
cur_dir='/home/arindam/Dropbox/FADE/src'

runfile='run.py'

transition_scenario=$3
transition_mode=1
output_dir="results"
location=$1
simulation_period=$2

cmd="python3 $runfile --location=$location --transition_scenario=$transition_scenario --simulation_period=$simulation_period --output_dir=$output_dir"

suffix='_buildings.csv'

cp $cur_dir/Trial_Data/age-distr.csv $facs_dir/covid_data/
cp $cur_dir/Trial_Data/$location$suffix $facs_dir/covid_data/
cd $facs_dir

$cmd | tee log.txt

datestamp=`date '+%F_%H:%M:%S'` 

suffix='--1.csv'
joiner='-'

cp $facs_dir/$output_dir/$location$joiner$transition_scenario$suffix $cur_dir/Results/$location$joiner$transition_scenario$joiner$datestamp$suffix

suffix1='-latest.csv'

cp $facs_dir/$output_dir/$location$joiner$transition_scenario$suffix $cur_dir/Results/$location$suffix1

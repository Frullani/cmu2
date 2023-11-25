set xrange [0:1]
set yrange [-17:1]
set title "p2 Plot"
plot 'p2_0.txt' with points pt 7 linecolor "red" title 'alpha=0', 'p2_1.txt' with points pt 7 linecolor "blue" title 'alpha=0.1', 'p2_2.txt' with points pt 7 linecolor "black" title 'alpha=1', 'p2_3.txt' with points pt 7 linecolor "yellow" title 'alpha=3'


BEGIN{id=0}
{
if (id != $1) {
	print $1;
	id=$1
	}
}

#ENSITIP

##structure d'un compte:

 - id discord
 - clef publique
 - clef privée
 - dernière transaction de 'stockage' (tx_in)
    - outpoint
	- hash
	- index (0 par defaut)
	- (script length)--> se recalcule
	- script --> signature + pubkey

import math
from CodonUsageIndices import SharpEcoliIndex
from Bio import Fasta

CodonsDict = {'TTT':0, 'TTC':0, 'TTA':0, 'TTG':0, 'CTT':0, 
'CTC':0, 'CTA':0, 'CTG':0, 'ATT':0, 'ATC':0, 
'ATA':0, 'ATG':0, 'GTT':0, 'GTC':0, 'GTA':0, 
'GTG':0, 'TAT':0, 'TAC':0, 'TAA':0, 'TAG':0, 
'CAT':0, 'CAC':0, 'CAA':0, 'CAG':0, 'AAT':0, 
'AAC':0, 'AAA':0, 'AAG':0, 'GAT':0, 'GAC':0, 
'GAA':0, 'GAG':0, 'TCT':0, 'TCC':0, 'TCA':0, 
'TCG':0, 'CCT':0, 'CCC':0, 'CCA':0, 'CCG':0, 
'ACT':0, 'ACC':0, 'ACA':0, 'ACG':0, 'GCT':0, 
'GCC':0, 'GCA':0, 'GCG':0, 'TGT':0, 'TGC':0, 
'TGA':0, 'TGG':0, 'CGT':0, 'CGC':0, 'CGA':0, 
'CGG':0, 'AGT':0, 'AGC':0, 'AGA':0, 'AGG':0, 
'GGT':0, 'GGC':0, 'GGA':0, 'GGG':0}


# this dictionary is used to know which codons encode the same AA.
SynonymousCodons = {'CYS': ['TGT', 'TGC'], 'ASP': ['GAT', 'GAC'],
'SER': ['TCT', 'TCG', 'TCA', 'TCC', 'AGC', 'AGT'],
'GLN': ['CAA', 'CAG'], 'MET': ['ATG'], 'ASN': ['AAC', 'AAT'],
'PRO': ['CCT', 'CCG', 'CCA', 'CCC'], 'LYS': ['AAG', 'AAA'],
'STOP': ['TAG', 'TGA', 'TAA'], 'THR': ['ACC', 'ACA', 'ACG', 'ACT'],
'PHE': ['TTT', 'TTC'], 'ALA': ['GCA', 'GCC', 'GCG', 'GCT'],
'GLY': ['GGT', 'GGG', 'GGA', 'GGC'], 'ILE': ['ATC', 'ATA', 'ATT'],
'LEU': ['TTA', 'TTG', 'CTC', 'CTT', 'CTG', 'CTA'], 'HIS': ['CAT', 'CAC'],
'ARG': ['CGA', 'CGC', 'CGG', 'CGT', 'AGG', 'AGA'], 'TRP': ['TGG'],
'VAL': ['GTA', 'GTC', 'GTG', 'GTT'], 'GLU': ['GAG', 'GAA'], 'TYR': ['TAT', 'TAC']}


class CodonAdaptationIndex:
	"""
	
	This class implements the codon adaptaion index (CAI) described by Sharp and
	Li (Nucleic Acids Res. 1987 Feb 11;15(3):1281-95).

	methods:

	set_cai_index(Index):

	This mehtod sets-up an index to be used when calculating CAI for a gene.
	Just pass a dictionary similar to the SharpEcoliIndex in CodonUsageIndices
	module.

	generate_index(FastaFile):

	This method takes a location of a FastaFile and generates an index. This
	index can later be used to calculate CAI of a gene.

	cai_for_gene(DNAsequence):

	This mehtod uses the Index (either the one you set or the one you generated)
	and returns the CAI for the DNA sequence.

	print_index():
	This method prints out the index you used.

	"""
	def __init__(self):
		self.index = {}
		self.codon_count={}
	
	# use this method with predefined CAI index
	def set_cai_index(self, Index):
		self.index = Index	
	
	def generate_index(self, FastaFile):
		# first make sure i am not overwriting an existing index:
		if self.index != {} or self.codon_count!={}:
			raise Error("an index has already been set or a codon count has been done. cannot overwrite either.")
		# count codon occurances in the file.
		self._count_codons(FastaFile)	
	
		# now to calculate the index we first need to sum the number of times
		# synonymous codons were used all together.
		for AA in SynonymousCodons.keys():
			Sum=0.0
			RCSU=[] # RCSU values are equal to CodonCount/((1/num of synonymous codons) * sum of all synonymous codons)
			
			for codon in SynonymousCodons[AA]:
				Sum += self.codon_count[codon]
			# calculate the RSCU value for each of the codons
			for codon in SynonymousCodons[AA]:
				RCSU.append(self.codon_count[codon]/((1.0/len(SynonymousCodons[AA]))*Sum))
			# now generate the index W=RCSUi/RCSUmax:
			RCSUmax = max(RCSU)
			for i in range(len(SynonymousCodons[AA])):
				self.index[SynonymousCodons[AA][i]]= RCSU[i]/RCSUmax
		
		
	def cai_for_gene(self, DNAsequence):
		caiValue = 0
		LengthForCai = 0
		# if no index is set or generated, the default SharpEcoliIndex will be used.
		if self.index=={}:
			self.set_cai_index(SharpEcoliIndex)
			
		if DNAsequence.islower():
			DNAsequence = DNAsequence.upper()
		for i in range (0,len(DNAsequence),3):
			codon = DNAsequence[i:i+3]
			if self.index.has_key(codon):
				if codon!='ATG' and codon!= 'TGG': #these two codons are always one, exclude them.
					caiValue += math.log(self.index[codon])
					LengthForCai += 1
			elif codon not in ['TGA','TAA', 'TAG']: # some indices you will use may not include stop codons.
				raise TypeError("illegal codon in sequence: %s.\n%s" % (codon, self.index))
		return math.exp(caiValue*(1.0/(LengthForCai-1)))
			
	def _count_codons(self, FastaFile):
		InputFile = open(FastaFile, 'r')
		# set up the fasta parser
		parser = Fasta.RecordParser()
		iterator = Fasta.Iterator(InputFile, parser)
		cur_record = iterator.next()
		
		# make the codon dictionary local
		self.codon_count = CodonsDict.copy()
		
		
		# iterate over sequence and count all the codons in the FastaFile.
		while cur_record:
			# make sure the sequence is lower case
			if cur_record.sequence.islower():
				DNAsequence = cur_record.sequence.upper()
			else:
				DNAsequence = cur_record.sequence
			for i in range(0,len(DNAsequence),3):
				codon = DNAsequence[i:i+3]
				if self.codon_count.has_key(codon):
					self.codon_count[codon] += 1
				else:
					raise TypeError("illegal codon %s in gene: %s" % (codon, cur_record.title))

			cur_record = iterator.next()
		InputFile.close()
	
	# this just gives the index when the objects is printed.
	def print_index (self):
		X=self.index.keys()
		X.sort()
		for i in X:
			print "%s\t%.3f" %(i, self.index[i])
		

import os, sys
from glob import glob
from ctakes_rest import process_sentence
from anafora import AnaforaData, AnaforaEntity
from os.path import basename,join

def main(args):
    if len(args) < 2:
        sys.stderr.write('2 required arguments: <input dir> <output dir>\n')
        sys.exit(-1)

    for filename in glob('%s/*.txt' % (args[0]) ):
        if filename.endswith('.txt'):
            fn = basename(filename[:-4]) # remove .txt
        else:
            fn = basename(filename)
        
        cur_id = 0
        print("Processing filename: %s" % (filename))

        anafora_data = AnaforaData()

        with open(filename, 'rt') as f:
            text = f.read()

        cuis = process_sentence(text)
        unique_spans = set()

        for cui_entry in cuis:
            begin, end = cui_entry[1], cui_entry[2]
            span_key = '%d-%d' % (begin, end)
            if span_key in unique_spans:
                continue
            
            unique_spans.add(span_key)
            annot = AnaforaEntity()
            annot.id = "%d@e@%s@ctakes" % (cur_id, fn)
            cur_id += 1
            annot.spans = ( (begin, end), )
            annot.type = "Concept"
            annot.parents_type = 'Entities'
            annot.properties['Status'] = ''
            anafora_data.annotations.append(annot)

        anafora_data.indent()
        os.makedirs(join(args[1], fn), exist_ok=True)
        anafora_data.to_file(join(args[1], fn, fn + '.leap_entity.ctakes.completed.xml'))


if __name__ == '__main__':
    main(sys.argv[1:])

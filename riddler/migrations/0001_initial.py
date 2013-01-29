# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Applicant'
        db.create_table('riddler_applicant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('riddler', ['Applicant'])

        # Adding model 'Series'
        db.create_table('riddler_series', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('instructions', self.gf('riddler.models.RichTextField')(null=True, blank=True)),
        ))
        db.send_create_signal('riddler', ['Series'])

        # Adding model 'Question'
        db.create_table('riddler_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['riddler.Series'])),
            ('question', self.gf('riddler.models.RichTextField')()),
            ('typical_duration', self.gf('django.db.models.fields.IntegerField')()),
            ('minimum_duration', self.gf('django.db.models.fields.IntegerField')()),
            ('prefilled_answer', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('editor_mode', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
        ))
        db.send_create_signal('riddler', ['Question'])

        # Adding model 'Test'
        db.create_table('riddler_test', (
            ('id', self.gf('django.db.models.fields.CharField')(default='q8T2', max_length=4, primary_key=True)),
            ('instructions', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('recruiter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('applicant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['riddler.Applicant'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('maximum_duration', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('cur_answer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='answered_by', null=True, to=orm['riddler.Answer'])),
            ('cur_series', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='answering_by', null=True, to=orm['riddler.Series'])),
        ))
        db.send_create_signal('riddler', ['Test'])

        # Adding M2M table for field series on 'Test'
        db.create_table('riddler_test_series', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('test', models.ForeignKey(orm['riddler.test'], null=False)),
            ('series', models.ForeignKey(orm['riddler.series'], null=False))
        ))
        db.create_unique('riddler_test_series', ['test_id', 'series_id'])

        # Adding model 'Answer'
        db.create_table('riddler_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['riddler.Test'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['riddler.Question'])),
            ('answer', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('start_to_answer_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('end_to_answer_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('riddler', ['Answer'])

        # Adding unique constraint on 'Answer', fields ['question', 'test']
        db.create_unique('riddler_answer', ['question_id', 'test_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Answer', fields ['question', 'test']
        db.delete_unique('riddler_answer', ['question_id', 'test_id'])

        # Deleting model 'Applicant'
        db.delete_table('riddler_applicant')

        # Deleting model 'Series'
        db.delete_table('riddler_series')

        # Deleting model 'Question'
        db.delete_table('riddler_question')

        # Deleting model 'Test'
        db.delete_table('riddler_test')

        # Removing M2M table for field series on 'Test'
        db.delete_table('riddler_test_series')

        # Deleting model 'Answer'
        db.delete_table('riddler_answer')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'riddler.answer': {
            'Meta': {'unique_together': "(('question', 'test'),)", 'object_name': 'Answer'},
            'answer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_to_answer_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['riddler.Question']"}),
            'start_to_answer_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['riddler.Test']"})
        },
        'riddler.applicant': {
            'Meta': {'object_name': 'Applicant'},
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'riddler.question': {
            'Meta': {'object_name': 'Question'},
            'editor_mode': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum_duration': ('django.db.models.fields.IntegerField', [], {}),
            'prefilled_answer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('riddler.models.RichTextField', [], {}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['riddler.Series']"}),
            'typical_duration': ('django.db.models.fields.IntegerField', [], {})
        },
        'riddler.series': {
            'Meta': {'object_name': 'Series'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('riddler.models.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'riddler.test': {
            'Meta': {'object_name': 'Test'},
            'applicant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['riddler.Applicant']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cur_answer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'answered_by'", 'null': 'True', 'to': "orm['riddler.Answer']"}),
            'cur_series': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'answering_by'", 'null': 'True', 'to': "orm['riddler.Series']"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'kctf'", 'max_length': '4', 'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'maximum_duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'recruiter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'series': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['riddler.Series']", 'symmetrical': 'False'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['riddler']